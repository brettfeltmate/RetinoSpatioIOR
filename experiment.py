# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLConstants import STROKE_CENTER, TK_MS, EL_GAZE_POS, EL_SACCADE_END
from klibs.KLUtilities import deg_to_px, now, pump
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
		# Stimuli are offset from each other by units of 6º
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
			"MissedSaccade": message("No eye movement detected!", blit_txt=False),
			"WrongSaccade":  message("Moved eyes in wrong direction!", blit_txt=False),
			"EarlyResponse": message("Please wait until the target appears to respond!", blit_txt=False)
		}

		self.rc.uses([KeyPressResponse])
		self.rc.keypress_listener.key_map = {"space": "space"}

 
		"""
		Sequence:

		Fixation  Cue      Saccade      Post-saccade gap  Target & Response
		|--------|--------|------------|-----------------|-----------------|
		500ms    300ms     600ms or TO  300ms             1500ms or TO
		"""

	def block(self):
		pass

	def setup_response_collector(self):
		self.rc.display_callback = self.monitor_behaviour
		self.rc.display_kwargs = {"phase": "target"}
		self.rc.interrupts = True

	def trial_prep(self):

		""" 		
		If participants are to make a prosaccade, the signal to saccade appears at the location the are to saccade to. Otherwise (for antisaccades) the signal appears at the location opposite. 
		"""
		if P.condition == "prosaccade":
			self.saccade_signal_loc = self.saccade_loc
			self.wrong_saccade_loc = "upper" if self.saccade_loc == "lower" else "lower"
		else:
			self.saccade_signal_loc = "upper" if self.saccade_loc == "lower" else "lower"
			self.wrong_saccade_loc = self.saccade_signal_loc

		""" 	
		Following upwards saccades, targets can appear at locations 1-6 otherwise, only 3 - 8. Initially cue location is selected from 1-6 if following a downwards saccade, 2 is added to the target position. 
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

		# self.el.drift_correct()
		self.bad_behaviour = None

	def trial(self):
		"""
		Sequence is basically: present the appropriate display, wait the appropriate time, then present the subsequent display. Participant's behaviour (gaze & pre-emptive responses) are monitored during waiting periods. 
		
		Upon detecting any untoward behaviour the trial is aborted, reshuffled into the trial deck, and the participant is admonished. 
		"""

		self.refresh_display(phase = "fixation")
		
		while self.evm.before("cue_onset"):
			self.monitor_behaviour(phase = "fixation")

		self.refresh_display(phase = 'cue')
		
		if P.development_mode: 
			any_key()

		while self.evm.before("cue_offset"):
			self.monitor_behaviour(phase = "cue")

		self.refresh_display(phase = 'fixation')
		
		if P.development_mode: 
			any_key()

		while self.evm.before("saccade_signal_onset"):
			self.monitor_behaviour(phase = "fixation")

		self.saccade_made = False

		self.refresh_display(phase = "saccade")

		if P.development_mode: 
			any_key()

		while self.evm.before("saccade_timeout"):
			self.monitor_behaviour(phase = 'saccade')
		
		# TODO: 
		# This needs to abort trial... best practice would be to refactor
		# self.monitor_behaviour() to handle this... but how...
		if not self.saccade_made:
			self.bad_behaviour = "MissedSaccade"

		else:
			# In the absence of a response, abort trial P.response_timeout (in ms) after detecting saccade.
			self.rc.terminate_after = [now() + P.response_timeout, TK_MS]
			
			# Present target and listen for response
			self.refresh_display(phase = "target")
			
			if P.development_mode: 
				any_key()
			
			self.rc.collect()

			return {
				"block_num": P.block_number,
				"trial_num": P.trial_number
			}

	def trial_clean_up(self):
		# Admonish participant if any undesered behaviour occurs.
		if self.bad_behaviour is not None:
			fill()
			blit(self.error_msgs[self.bad_behaviour], registration=5, location=P.screen_c)
			flip()
			any_key()

	def clean_up(self):
		pass

	# Update display to reflect current trial event.
	def refresh_display(self, phase):
		fill()
		# Present all placeholders
		# If cue: present cued placholder in its respective location
		for key, val in self.locations['placeholders'].items():
			
			if key == self.cue_loc and phase == 'cue':
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
			if key == self.saccade_signal_loc and phase == "saccade":
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
		# If previous check detected unwanted behaviour, abort trial
		if self.bad_behaviour != None:
			raise TrialException(self.error_msgs[self.bad_behaviour])

		# Prior to repsonse period, monitor for system commands or early responses
		if phase != "target":
			# grab keyboard events
			key_events = pump(True)
			# Check for system commands
			ui_request(queue=key_events)
			# Check for early responding
			if key_pressed(key='space', queue=key_events):
				self.bad_behaviour = "EarlyResponse"



		# Pull gaze behaviour from eyelink 
		e = self.el.get_event_queue()
		# During fixation & cue phase, gaze should not depart from central fixation.
		if phase in ['fixation', 'cue']:
			if not self.el.within_boundary(label='center', valid_events = [EL_GAZE_POS], event_queue=e):
				self.bad_behaviour = "BrokeFixation"
		
		# During target phase, gaze should not depart from the saccaded to fixation
		elif phase == "target":
			if not self.el.within_boundary(label=self.saccade_loc, valid_events = [EL_GAZE_POS], event_queue=e):
				self.bad_behaviour = 'BrokeFixation'
		# period during which participants must saccade to the new fixation point
		else: 
			# If the correct saccade is made, great
			# TODO: log saccade info
			if self.el.saccade_to_boundary(label=self.saccade_loc, event_queue=e) is not False:
				self.saccade_made = True
			# Abort if participant saccades to the wrong location
			elif self.el.saccade_to_boundary(label=self.wrong_saccade_loc, event_queue=e) is not False:
				self.bad_behaviour = "WrongSaccade"
			# Remaining at the central fixation doesn't count as an error, until the saccade window elapses; if self.saccade_made is not set to true, trial will abort pre-target onset
			elif self.el.within_boundary(label='center', valid_events = [EL_GAZE_POS], event_queue=e):
				return
			# If participant looks anywhere other than central or intended fixation, abort
			else:
				self.bad_behaviour = "BrokeFixation"
		
		