from klibs.KLIndependentVariable import IndependentVariableSet

RetinoSpatioIOR_ind_vars = IndependentVariableSet()

# To which location participants must make a saccade
# NOTE:
# Which saccade location is cued depends on partipant condition
# Pro-saccade: matches location of cue
# Anti-saccade: opposite location is cued
RetinoSpatioIOR_ind_vars.add_variable("saccade_loc", str)
RetinoSpatioIOR_ind_vars["saccade_loc"].add_values("lower", "upper")

# Indicates which placeholder is cued on trial
RetinoSpatioIOR_ind_vars.add_variable("cue_loc", int)
RetinoSpatioIOR_ind_vars['cue_loc'].add_values(3, 4, 5, 6)

# Indicates location at which target is presented
# NOTE: this is conditional on the location to which saccades are made
# in that targets only appear in one of the six locations closest
# to the saccade location. When participants saccade to the lower
# fixation point, 2 is added to the target loc (i.e., appears at 3-8)
RetinoSpatioIOR_ind_vars.add_variable("target_loc", int)
RetinoSpatioIOR_ind_vars['target_loc'].add_values(1, 2, 3, 4, 5, 6)