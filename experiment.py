# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLConstants import STROKE_CENTER
from klibs.KLUtilities import deg_to_px
from klibs.KLGraphics import KLDraw as kld

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

class RetinoSpatioIOR(klibs.Experiment):

	def setup(self):
		offset = deg_to_px(6)

		"""
		Layout
		Offset - Stimuli offset in increments of 6º along cardinal directions, respective to screen centre
		[] - Placeholders, 1.5º
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


		self.locations = {
			'placeholders': {
				0: [P.screen_c[0] - offset, P.screen_c[1] - (offset*3)],
				1: [P.screen_c[0] + offset, P.screen_c[1] - (offset*3)],
				2: [P.screen_c[0] - offset, P.screen_c[1] - offset],
				3: [P.screen_c[0] + offset, P.screen_c[1] - offset],
				4: [P.screen_c[0] - offset, P.screen_c[1] + offset],
				5: [P.screen_c[0] + offset, P.screen_c[1] + offset],
				6: [P.screen_c[0] - offset, P.screen_c[1] + (offset * 3)],
				7: [P.screen_c[0] + offset, P.screen_c[1] + (offset * 3)],
			},
			'fixation': {
				'upper': [P.screen_c[0], P.screen_c[1] - (offset*2)],
				'middle': P.screen_c,
				'lower': [P.screen_c[0], P.screen_c[1] + (offset*2)],
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

		uncued_stroke = [deg_to_px(0.1), WHITE, STROKE_CENTER]
		cued_stroke = [deg_to_px(0.3), WHITE, STROKE_CENTER]

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

		"""
		Eye-tracker boundaries (for checking fixation & saccade locations)
		
		Boundaries:
			Fixation-middle
			Fixation-upper
			Fixation-lower
		"""





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
		pass

	def block(self):
		pass

	def setup_response_collector(self):
		pass

	def trial_prep(self):
		pass

	def trial(self):
		"""
		:return:

		saccade_condition: pro OR anti
		saccade_cue_loc: up OR down
		target_cue_loc:

		"""

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass
