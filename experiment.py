# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLConstants import STROKE_CENTER, TK_MS, EL_GAZE_POS, EL_SACCADE_END
from klibs.KLUtilities import deg_to_px, now, pump, flush
from klibs.KLUserInterface import ui_request, key_pressed, any_key
from klibs.KLGraphics import fill, blit, flip
from klibs.KLGraphics import KLDraw as kld
from klibs.KLBoundary import CircleBoundary
from klibs.KLCommunication import message
from klibs.KLResponseCollectors import KeyPressResponse
from klibs.KLExceptions import TrialException

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

class RetinoSpatioIOR(klibs.Experiment):

	def setup(self):

		"""
		Layout
		Offset - Stimuli offset in increments of 6º along cardinal directions, respective to screen centre
		[] - Placeholders, 1.5º; denoted 0-7 from top-left to bottom-right
		() - Saccade locations, 1.5º
		+  - Fixation, 1.5º
		*  - Target, 0.75º

		[]             []

			    ()

		[*]            []

			     +

		[]             []

			    ()

		[]             []
		"""
		# Stimuli are offset from each other by units of 6º, but are brought in when developing (small screen)
		offset = deg_to_px(3) if P.development_mode else deg_to_px(6)

		# Point positions to serve as anchors when positioning stimuli
		self.locations = {
			'placeholders': {
				# location : [x, y]
				1: (P.screen_c[0] - offset, P.screen_c[1] - (offset*1.5)),
				2: (P.screen_c[0] + offset, P.screen_c[1] - (offset*1.5)),
				3: (P.screen_c[0] - offset, P.screen_c[1] - (offset*0.5)),
				4: (P.screen_c[0] + offset, P.screen_c[1] - (offset*0.5)),
				5: (P.screen_c[0] - offset, P.screen_c[1] + (offset*0.5)),
				6: (P.screen_c[0] + offset, P.screen_c[1] + (offset*0.5)),
				7: (P.screen_c[0] - offset, P.screen_c[1] + (offset*1.5)),
				8: (P.screen_c[0] + offset, P.screen_c[1] + (offset*1.5)),
			},
			# Gaze & saccade locations
			'fixation': {
				'upper': (P.screen_c[0], P.screen_c[1] - offset),
				'center': P.screen_c,
				'lower': (P.screen_c[0], P.screen_c[1] + offset),
			}
		}


		"""
		Stimuli:
		[] - Placeholders, 1.5º
		() - Saccade targets, 1.5º
		+  - Fixation, 1.5º
		*  - Target, 0.75º
		Cue - Thickening of placeholder
		"""

		# uncued = default stroke, cued = only applied to the cued location
		uncued_stroke = [deg_to_px(0.1), WHITE, STROKE_CENTER]
		cued_stroke = [deg_to_px(0.3), WHITE, STROKE_CENTER]

		# Visual assets
		self.stimuli = {
			"placeholder":
				kld.Rectangle(
					width=deg_to_px(1.5),
					stroke=uncued_stroke),
			"cued_placeholder":
				kld.Rectangle(
					width=deg_to_px(1.5),
					stroke=cued_stroke,
				),
			"fixation":
				kld.FixationCross(
					size=deg_to_px(1.5),
					thickness=deg_to_px(0.1),
					stroke=uncued_stroke
				),
			"cued_fixation":
				kld.FixationCross(
					size=deg_to_px(1.5),
					thickness=deg_to_px(0.1),
					stroke=cued_stroke
				),
			"target":
				kld.Circle(
					diameter=deg_to_px(0.75),
					fill=WHITE
				)
		}

		
		# Eye-tracker boundaries (for montoring fixations & saccades)
		self.el.add_boundaries(boundaries = [
			CircleBoundary(
				label = "upper", 
				center = self.locations["fixation"]['upper'], 
				radius = deg_to_px(3)
			),
			CircleBoundary(
				label = "center",
				center = self.locations['fixation']['center'],
				radius = deg_to_px(3)
			),
			CircleBoundary(
				label = "lower",
				center = self.locations['fixation']['lower'],
				radius = deg_to_px(3)
			)
		])

		# Error messages
		self.error_msgs = {
			"BrokeFixation":  message("Moved eyes too soon!", blit_txt=False),
			"MissedSaccade":  message("No eye movement detected!", blit_txt=False),
			"WrongSaccade":   message("Moved eyes in wrong direction!", blit_txt=False),
			"EarlyResponse":  message("Please wait until the target appears to respond!", blit_txt=False)
		}

		self.rc.uses([KeyPressResponse])
		self.rc.keypress_listener.key_map = {"space": "space"}

		# Establish block sequence
		base = ['pro', 'anti'] if P.condition == 'pro' else ['anti', 'pro']
		self.block_sequence = [item for item in base for i in range(P.blocks_per_condition)]

		if P.run_practice_blocks:
			# Add extra blocks if running practice trials
			self.insert_practice_block(block_nums=[1, 6], trial_counts=P.trials_per_practice)

	def block(self):
		self.block_condition = self.block_sequence.pop(0)

		if P.practicing:
			fill()
			message("This is a practice block", blit_txt=True, location=P.screen_c, registration=5)
			flip()

			any_key()

		fill()
		if self.block_condition == 'pro':
			message("For this block, make prosaccades towards the cue.", 
	   			blit_txt=True, location=P.screen_c, registration=5
			)
		else:
			message("For this block, make antisaccades away from the cue.", 
	   			blit_txt=True, location=P.screen_c, registration=5
			)

		flip()
		any_key()

		fill()
		message("any key to start", blit_txt=True, location=P.screen_c, registration=5)
		flip()

		any_key()

	def setup_response_collector(self):
		self.rc.display_callback = self.monitor_behaviour
		self.rc.display_kwargs = {"phase": "target"}
		self.rc.interrupts = True

	def trial_prep(self):

		""" 		
		If participants are to make a prosaccade, the signal to saccade appears at the location the are to saccade to. Otherwise (for antisaccades) the signal appears at the location opposite. 
		"""
		if self.block_condition == "pro":
			self.saccade_signal_loc = self.saccade_loc
			self.wrong_saccade_loc = "upper" if self.saccade_loc == "lower" else "lower"
		else:
			self.saccade_signal_loc = "upper" if self.saccade_loc == "lower" else "lower"
			self.wrong_saccade_loc = self.saccade_signal_loc

		""" 	
		Following upwards saccades, targets can appear at locations 1-6 otherwise, only 3 - 8. Initially cue location is selected from 1-6. If following a downwards saccade, 2 is added to the target position. 
		"""
		if self.saccade_loc == 'upper':
			self.target_location = self.target_loc
		else:
			self.target_location = self.target_loc + 2


		"""
		Event sequence:

		Fixation  Cue      Saccade      Post-saccade gap  Target & Response
		|--------|--------|------------|-----------------|-----------------|
		500ms    300ms     600ms or TO  300ms             1500ms or TO

		NOTE: Onset time of remaining events (target & response) are conditional on time of re-fixation, so will be handled in trial()
		"""
		events = []
		events.append([P.fixation_duration, "cue_onset"])
		events.append([events[-1][0] + P.cue_duration, "cue_offset"])
		events.append([events[-1][0] + P.cue_saccade_onset_asynchrony, "saccade_signal_onset"])
		events.append([events[-1][0] + P.saccade_timeout, "saccade_timeout"])

		# Register event sequence w/ event manager
		for e in events:
			self.evm.register_ticket([e[1], e[0]])

		self.el.drift_correct()

	def trial(self):
		"""
		Sequence is basically: present the appropriate display, wait the appropriate time, then present the subsequent display. Participant's behaviour (gaze & pre-emptive responses) are monitored during waiting periods. 
		
		Upon detecting any untoward behaviour the trial is aborted, reshuffled into the trial deck, and the participant is admonished. 
		"""

		self.refresh_display(phase = "fixation")
		
		flush()
		while self.evm.before("cue_onset"):
			self.monitor_behaviour(phase = "fixation")

		self.refresh_display(phase = 'cue')

		flush()
		while self.evm.before("cue_offset"):
			self.monitor_behaviour(phase = "cue")

		self.refresh_display(phase = 'fixation')

		flush()
		while self.evm.before("saccade_signal_onset"):
			self.monitor_behaviour(phase = "fixation")

		self.saccade_made = False

		self.refresh_display(phase = "saccade")

		flush()
		while self.evm.before("saccade_timeout") and not self.saccade_made:
			self.monitor_behaviour(phase = 'saccade')
		
		# TODO: 
		# This needs to abort trial... best practice would be to refactor
		# self.monitor_behaviour() to handle this... but how...
		if not self.saccade_made:
			self.abort_and_recycle_trial("MissedSaccade")

		else:
			self.refresh_display(phase='fixation')

			target_onset = now() + (P.saccade_target_onset_asynchrony * 0.001) # milliseconds

			flush()
			while now() < target_onset:
				self.monitor_behaviour(phase='target')

			# In the absence of a response, abort trial P.response_timeout (in ms) after detecting saccade.
			self.rc.terminate_after = [now() + P.response_timeout, TK_MS]
			
			# Present target and listen for response
			self.refresh_display(phase = "target")
			
			self.rc.collect()
			rt = self.rc.keypress_listener.response(value=False)

			return {
				"block_num": P.block_number,
				"trial_num": P.trial_number,
				"condition": self.block_condition,
				"cue_location": self.cue_loc,
				"saccade_location": self.saccade_loc,
				"target_location": self.target_location,
				"rt": rt
			}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass

	def abort_and_recycle_trial(self, err_type):
		flush()

		fill()
		blit(self.error_msgs[err_type], registration=5, location=P.screen_c)
		flip()

		any_key()

		err_data = {
			"participant_id": P.participant_id,
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "condition": self.block_condition,
            "cue_location": self.cue_loc,
	    	"saccade_location": self.saccade_loc,
            "target_location": self.target_location,
            "err_type": err_type
		}

		self.database.insert(data=err_data, table="errors")
		raise TrialException(self.error_msgs[err_type])



	# Update display to reflect current trial event.
	def refresh_display(self, phase):
		fill()
		# Present all placeholders
		# If cue: present cued placholder in its respective location
		for key, val in self.locations['placeholders'].items():
			
			if phase == 'cue' and key == self.cue_loc:
				to_blit = 'cued_placeholder'
			else:
				to_blit = 'placeholder'

			blit(
				self.stimuli[to_blit],
				registration=5,
				location=val
			)
		
		# Same for fixation crosses
		for key, val in self.locations['fixation'].items():
			if phase == "saccade" and key == self.saccade_signal_loc:
				to_blit = 'cued_fixation'
			else:
				to_blit = 'fixation'

			blit(
				self.stimuli[to_blit],
				registration=5,
				location=val,
			)
			
		# When needed, present target within it's respective placeholder
		if phase == 'target':
			blit(
				self.stimuli['target'],
				registration=5,
				location=self.locations["placeholders"][self.target_location]
			)

		flip()

	
	def monitor_behaviour(self, phase):
		# Prior to repsonse period, monitor for system commands or early responses
		if phase != "target":
			# grab keyboard events
			key_events = pump(True)
			# Check for system commands
			ui_request(queue=key_events)
			# Check for early responding
			if key_pressed(key='space', queue=key_events):
				self.abort_and_recycle_trial("EarlyResponse")



		# Pull gaze behaviour from eyelink 
		e = self.el.get_event_queue()
		# During fixation & cue phase, gaze should not depart from central fixation.
		if phase in ['fixation', 'cue']:
			if not self.el.within_boundary('center', [EL_GAZE_POS], e):
				self.abort_and_recycle_trial("BrokeFixation")
		
		# During target phase, gaze should not depart from the saccaded to fixation
		elif phase == "target":
			if not self.el.within_boundary(self.saccade_loc, [EL_GAZE_POS], e):
				self.abort_and_recycle_trial('BrokeFixation')
		# period during which participants must saccade to the new fixation point
		else: 
			if self.el.within_boundary(self.saccade_loc, [EL_GAZE_POS, EL_SACCADE_END], e):
				self.saccade_made = True

			elif self.el.within_boundary(self.wrong_saccade_loc, [EL_GAZE_POS, EL_SACCADE_END], e):
				self.abort_and_recycle_trial("WrongSaccade")

			else:
				pass
		
		