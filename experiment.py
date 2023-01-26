# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLConstants import STROKE_CENTER
from klibs.KLUtilities import deg_to_px 
from klibs.KLGraphics import fill, blit, flip
from klibs.KLGraphics import KLDraw as kld
from klibs.KLBoundary import BoundarySet, CircleBoundary
from klibs.KLCommunication import message
from klibs.KLResponseCollectors import KeyPressResponse

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
		offset = deg_to_px(6)

		# Point positions to serve as anchors when positioning stimuli
		self.locations = {
			'placeholders': {
				1: (P.screen_c[0] - offset, P.screen_c[1] - (offset*1.5)),
				2: (P.screen_c[0] + offset, P.screen_c[1] - (offset*1.5)),
				3: (P.screen_c[0] - offset, P.screen_c[1] - offset),
				4: (P.screen_c[0] + offset, P.screen_c[1] - offset),
				5: (P.screen_c[0] - offset, P.screen_c[1] + offset),
				6: (P.screen_c[0] + offset, P.screen_c[1] + offset),
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
				kld.Annulus(
					diameter=deg_to_px(0.75),
					thickness=deg_to_px(0.1),
					fill=WHITE
				)
		}

		
		# Eye-tracker boundaries (for montoring fixations & saccades)
		self.gaze = BoundarySet([
			CircleBoundary(
				label = "upper", 
				center = self.locations["fixation"]['upper'], 
				radius = deg_to_px(1.5)
			),
			CircleBoundary(
				label = "center",
				center = self.locations['fixation']['center'],
				radius = deg_to_px(1.5)
			),
			CircleBoundary(
				label = "lower",
				center = self.locations['fixation']['lower'],
				radius = deg_to_px(1.5)
			)
		])


		self.error_msgs = {
			"EarlySaccade":  message("Moved eyes too soon!", blit_txt=False),
			"MissedSaccade": message("No eye movement detected!", blit_txt=False),
			"WrongSaccade":  message("Moved eyes in wrong direction!", blit_txt=False),
			"EarlyResponse": message("Please wait until the target appears to respond!", blit_txt=False)
		}

		self.rc.uses[KeyPressResponse]
		self.rc.keypress_listener.key_map = {"spacebar": "spacebar"}

 
		"""

		Sequence:

		Fixation  Cue      Saccade      Post-saccade gap  Target & Response
		|--------|--------|------------|-----------------|-----------------|
		500ms    300ms     600ms or TO  300ms             1500ms or TO

		Checks / errors (recycled)
		- Drift calibration
		- Early saccade
		- Missed saccade
		- Incorrect saccade
		- Departures from fixation


		"""

	def block(self):
		pass

	def setup_response_collector(self):
		# I don't think anything needs to go here
		pass

	def trial_prep(self):
		# Set location of saccade cue (dependent on pro/anti group)
		# Set location of target (dependent on saccade location)

		
		pass

	def trial(self):
		"""
		:return:
		practicing: True or False
		saccade_condition: pro or anti
		saccade_cue_loc: up or down
		target_cue_loc: 3-6
		target_loc: 1-8
		button_rt
		saccade_rt



		"""

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass
