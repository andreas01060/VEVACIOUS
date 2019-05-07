# This Python program was automatically generated by Vevacious, a program
# released under the GNU General Public License, and, as such, this program
# is also under the GNU General Public License. Please see the
# README.Vevacious.txt file accompanying the Vevacious C++ code for a full
# list of files, brief documentation, and further details on the license.
#
# Vevacious authors: Ben O'Leary (benjamin.oleary@gmail.com)
#                    Florian Staub (florian.staub@googlemail.com)
#                    Jose' Eliel Camargo Molina (elielx@gmail.com)
#                    Werner Porod (porod@physik.uni-wuerzburg.de)
#
#      Copyright 2012 Ben O'Leary, Florian Staub,
#                     Jose' Eliel Camargo Molina, Werner Porod
#
# (B.O'L. would like to apologize about the state of this file: ideally it
# would be a lot neater, and respect modern programming practices. Maybe a
# later version will tidy it up properly...)
#
#
from __future__ import division
import math
import numpy
import VevaciousParameterDependent as VPD
import VevaciousTreeLevelExtrema as VTE


treeLevelExtrema = VTE.pointsToTry
vcs = VPD.Vevacious(
                EffectivePotential = VPD.TreeLevelPotential )
# Various settings can be changed here: e.g. to use the tree-level
# potential for minimizing and tunneling, one could use
# EffectivePotential = VPD.TreeLevelPotential
# Even a custom potential function can be inserted here, as long as it LoopAndThermalCorrectedPotential
# takes the correct arguments. Have a look at
# VevaciousParameterDependent.py to see the correct format.LoopAndThermalCorrectedPotential
# IF YOU DO USE THE TREE-LEVEL POTENTIAL, PLEASE REMEMBER TO TURN OFF
# THERMAL CALCULATIONS! The thermal corrections are formally a loop effect,
# and the tree-level potential is independent of the temperature. This
# means that Vevacious would spend forever trying to find the critical
# temperature at which tunneling from the DSB minimum to the panic vacuum
# becomes impossible This can just be set by uncommenting the next line.
#vcs.ShouldTunnelThermally = False
vcs.allowedRunningTime = 3600.0
# Allowing an hour of running time is maybe excessive...
vcs.SetMinuitLimits( 20.0 * VPD.energyScale )
# MINUIT is now not allowed to roll outside a hypercube defined by all the
# field values being less than five times the renormalization scale.
# WriteExtrema is not important for deciding whether a parameter point is
# metastable, but it helps with debugging.
vcs.WriteExtrema( treeLevelExtrema, "Vevacious_tree-level_extrema.txt" )

# RollExtrema includes the automatic nudging off saddle points according to
# vcs.nudgeList.
# It also sorts the minima and sets vcs.panicVacuum and vcs.globalMinimum,
# and vcs.dsbVacuumIsMetastable.
vcs.RollExtrema( treeLevelExtrema )
print( "DSB vacuum: " + vcs.ExtremumAsMathematica( vcs.dsbVacuum ) )

# WriteMinima is also not important for deciding whether a parameter point
# is metastable, but it helps with debugging.
vcs.WriteMinima( "Vevacious_loop-corrected_minima.txt" )

metastabilityVerdict = "not_calculated"
quantumTunnelingActionType = "not_calculated"
quantumStabilityVerdict = "not_calculated"
thermalStabilityVerdict = "not_calculated"
alreadyExcluded = False
exclusionTemperatureString = "not_calculated"
quantumTunnelingTimeInUniverseAgesString = "not_calculated"
thermalTunnelingSurvivalProbabilityString = "not_calculated"
slhaSummaryCode = -99


if ( not vcs.dsbVacuumIsMetastable ):
    print( "DSB vacuum is stable (as far as the model file allows)." )
    metastabilityVerdict = "stable"
    quantumTunnelingActionType = "unnecessary"
    quantumStabilityVerdict = "stable"
    thermalStabilityVerdict = "stable"
    exclusionTemperatureString = "unnecessary"
    quantumTunnelingTimeInUniverseAgesString = "-1.0"
    thermalTunnelingSurvivalProbabilityString = "1.0"
    slhaSummaryCode = 1
else:
# The deepest minimum found by vcs.RollExtrema is recorded as
# vcs.globalMinimum and it may happen to correspond to the DSB minimum.
# If there were minima found which are deeper than the DSB minimum, the one
# closest to the DSB minimum (or reflections of it in any field value, as
# the potential may be invariant under a set of sign flips of the fields)
# is recorded as the panic vacuum, in vcs.panicVacuum. The panic vacuum
# does not necessarily correspond to vcs.globalMinimum. If "tunnel_to_global" is set
# to "True" the global minimum will always be set as vcs.panicVacuum. Strictly, all
# minima should be checked for tunneling, but it is computationally
# expensive, and it seems that for points of phenomenological interest, the
# bubble wall is the dominant term so the closest minima are more likely to
# have the lowest actions.
    print( "Panic vacuum: "
           + vcs.ExtremumAsMathematica( vcs.panicVacuum ) )
    print( "Global minimum found: "
           + vcs.ExtremumAsMathematica( vcs.globalMinimum )
           + "\n\n" )
    metastabilityVerdict = "metastable"
    slhaSummaryCode = 0


if ( vcs.dsbVacuumIsMetastable
     and
     vcs.ShouldTunnel ):
# First, a direct path between the minima is taken to get an upper bound on
# the bounce action.
    quantumTunnelingActionType = "direct_path"
    quantumStabilityVerdict = "long-lived"
    vcs.SetTemperature( 0.0 )
    quantumAction = vcs.CalculateAction( falseVacuum = vcs.dsbVacuum,
                                         trueVacuum = vcs.panicVacuum,
                                         deformPath = False,
                                         thermalNotQuantum = False )
    print( "Direct path zero-temperature 4-dimensional action is "
           + str( quantumAction )
           + "\n\n" )
    quantumTunnelingTimeInUniverseAgesString = str(
                      vcs.QuantumTunnelingTimeInInverseGev( quantumAction )
                                     / vcs.ageOfKnownUniverseInInverseGev )
    alreadyExcluded = ( quantumAction <= vcs.quantumActionThreshold )
    if alreadyExcluded:
        quantumStabilityVerdict = "short-lived"
        thermalStabilityVerdict = "low_survival_probability"
        slhaSummaryCode = -1
    elif vcs.ShouldTunnelThermally:
        thermalStabilityVerdict = "high_survival_probability"
        optimalTunnelingTemperature = 0.0
# If the parameter point is not excluded by the naive straight path at zero
# temperature, then we check thermal tunneling by direct paths to see if
# a direct path can exclude the point, & to get an estimate of what
# temperature to use for a full calculation with path deformation.
        print( "Upper bound on zero-temperature full effective action by"
               + " direct path is too high to exclude point, so trying"
               + " direct paths at non-zero temperatures." )
        dsbEvaporationTemperature = vcs.FindEvaporationTemperature(
                                                             vcs.dsbVacuum,
                                                                    2,
                                                               False )[ 1 ]
        if not ( dsbEvaporationTemperature > 0.0 ):
            thermalStabilityVerdict = "low_survival_probability"
            exclusionTemperatureString = str( dsbEvaporationTemperature )
            alreadyExcluded = True
            dsbDepth = VPD.FunctionFromDictionary( vcs.EffectivePotential,
                                          vcs.dsbVacuum[ "FieldValues" ],
                                                   0.0 )
            originDepth = VPD.FunctionFromDictionary(
                                                    vcs.EffectivePotential,
                                                      VPD.fieldOrigin,
                                                      0.0 )
            vcs.LogWarning( "Point with all fields = 0 is deeper ("
                            + str( originDepth )
                            + " GeV^4) than DSB vacuum ("
                            + str( dsbDepth )
                            + " GeV^4) at T = 0!" )
        else:
            criticalTemperatureRange = vcs.FindEvaporationTemperature(
                                                           vcs.panicVacuum,
                                                                       8,
                                                                     True )
# The critical temperature is above criticalTemperatureRange[ 0 ] and below
# criticalTemperatureRange[ 1 ], and the range should be no more than
# 2^(-logTwoAccuracy) times the critical temperature in extent.
            fitNodes = 3
            lowestFitTemperature = dsbEvaporationTemperature
# We assume that the optimal tunneling temperature will be above the DSB
# evaporation temperature, but if the DSB evaporation temperature is close
# enough to the critical temperature, we include temperatures below it for
# the fit, even though it introduces a kink which is actually pretty badly
# approximated by a polynomial. (If the DSB evaporation temperature is
# higher than the panic vacuum's evaporation temperature, then there is no
# kink and we consider a lower resolution polynomial, across the range
# from 1 GeV up to 0.9 times the panic evaporation temperature.)
            if ( ( criticalTemperatureRange[ 0 ]
                   / dsbEvaporationTemperature ) < 2.0 ):
                lowestFitTemperature = 1.0
                if ( criticalTemperatureRange[ 0 ]
                     > dsbEvaporationTemperature ):
                    fitNodes = 10
            temperatureFitDifference = ( 0.9
                                         * ( criticalTemperatureRange[ 0 ]
                                             - lowestFitTemperature ) )
            temperaturesForFit = [ ( lowestFitTemperature
                                     + ( ( stepIndex
                                           * temperatureFitDifference )
                                         / ( fitNodes - 1.0 ) ) )
                                   for stepIndex in range( fitNodes ) ]
            [ optimalTunnelingTemperature,
              alreadyExcluded,
              thermalTunnelingSurvivalProbabilityString
                                   ] = vcs.FindOptimalTunnelingTemperature(
                                                        temperaturesForFit,
                                             criticalTemperatureRange[ 0 ],
                                             criticalTemperatureRange[ 1 ],
                                                dsbEvaporationTemperature )
            exclusionTemperatureString = str(
                                              optimalTunnelingTemperature )
# vcs.FindOptimalTunnelingTemperature fits n = len( temperaturesForFit )
# coefficents a_1 to a_n for a function
# a_1 (Tc - T )^(-2) + a_2 T^0 + a_3 T + ...
# to approximate the temperature (T) dependence (where Tc is the criticial
# temperature) of the 3-dimensional thermal action calculated by a direct
# path in field space, which is then minimized by PyMinuit to find an
# estimate of the optimal tunneling temperature. It also returns True if
# the cautiously-high estimate of the survival probability at any of the
# given temperatures is below the threshold given by the Vevacious
# initialization XML file.
        if alreadyExcluded:
            thermalStabilityVerdict = "low_survival_probability"
            slhaSummaryCode = -2


    if ( vcs.ShouldDeformTunnelPaths
         and
         ( not ( alreadyExcluded
                 or
                 vcs.AllowedRunningTimeExceeded() ) ) ):
# Here we continue to check the zero-temperature quantum tunneling (if the
# direct path at zero temperature did not already exclude the point):
        vcs.SetTemperature( 0.0 )
        quantumAction = vcs.CalculateAction( falseVacuum = vcs.dsbVacuum,
                                             trueVacuum = vcs.panicVacuum,
                                             deformPath = True,
                                             thermalNotQuantum = False,
                                             innerLoopMaxDeformations = 10,
                                            outerLoopMaxDeformations = 10 )
# CosmoTransitions nests a loop of deformations inside a loop for some
# unclear reason. The arguments passed here are intentionally low, as the
# path deformation takes a _very_ long time, and the returns on further
# iterations usually diminish very quickly.
        quantumTunnelingActionType = "deformed_path"
        print( "Final deformed path zero-temperature 4-dimensional"
               + " action is "
               + str( quantumAction )
               + " units of h-bar.\n\n" )
        quantumTunnelingTimeInInverseGev = (
                                      vcs.QuantumTunnelingTimeInInverseGev(
                                                          quantumAction ) )
        print( "Zero-temperature tunneling time in 1/GeV = "
               + str( quantumTunnelingTimeInInverseGev ) )
        print( "Age of known Universe in 1/GeV = "
               + str( vcs.ageOfKnownUniverseInInverseGev ) )
        quantumTunnelingTimeInUniverseAges = (
                                           quantumTunnelingTimeInInverseGev
                                     / vcs.ageOfKnownUniverseInInverseGev )
        quantumTunnelingTimeInUniverseAgesString = str(
                                       quantumTunnelingTimeInUniverseAges )
        print( "Tunneling time in Universe-ages = "
               + quantumTunnelingTimeInUniverseAgesString )
        quantumTunnelingTimeInSeconds = str(
                                            vcs.ageOfKnownUniverseInSeconds
                                     * quantumTunnelingTimeInUniverseAges )
        print( "Zero-temperature tunneling time estimate is "
               + quantumTunnelingTimeInSeconds
               + " seconds (age of known Universe = "
               + str( vcs.ageOfKnownUniverseInSeconds )
               + " seconds).\n\n" )
        if ( quantumAction < vcs.quantumActionThreshold ):
            quantumStabilityVerdict = "short-lived"
            slhaSummaryCode = -1
        elif ( vcs.ShouldTunnelThermally
               and
               ( not vcs.AllowedRunningTimeExceeded() ) ):
# If the parameter point was not excluded just by quantum tunneling, we
# calculate whether fully deformed thermal tunneling excludes it.

            vcs.SetTemperature( optimalTunnelingTemperature )
            print( "Deforming tunneling path at temperature "
                   + str( optimalTunnelingTemperature )
                   + " GeV." )
            print( "At this temperature, the threshold 3-dimensional"
                   + " action is "
                   + str( optimalTunnelingTemperature
                          * ( vcs.thermalActionOverTemperatureComparison
                              - math.log( optimalTunnelingTemperature ) ) )
                   + " GeV (aggressive; a cautious threshold is less by"
                   + " roughly ten times "
                   + str( optimalTunnelingTemperature )
                   + " GeV).\n\n" )
            thermalAction = vcs.CalculateAction(
                                               falseVacuum = vcs.dsbVacuum,
                                              trueVacuum = vcs.panicVacuum,
                                                deformPath = True,
                                                thermalNotQuantum = True,
                                             innerLoopMaxDeformations = 10,
                                            outerLoopMaxDeformations = 10 )
            print( "Final 3-dimensional action  at this temperature = "
                   + str( thermalAction )
                   + " GeV.\n\n" )
            if not ( thermalAction > 0.0 ):
                thermalStabilityVerdict = "unsure_survival_probability"
                slhaSummaryCode = -3
                print( "CosmoTransitions seems to have failed to"
                       + " converge: marking the survival probability as"
                       + "uncertain.\n\n" )
            if ( ( ( thermalAction / optimalTunnelingTemperature )
                     + math.log( thermalAction ) )
                   < vcs.thermalActionOverTemperatureComparison ):
                thermalStabilityVerdict = "low_survival_probability"
                slhaSummaryCode = -2
            elif ( ( ( thermalAction / optimalTunnelingTemperature )
                     + math.log( optimalTunnelingTemperature ) )
                   < vcs.thermalActionOverTemperatureComparison ):
                thermalStabilityVerdict = "unsure_survival_probability"
                slhaSummaryCode = -3
            print( "Temperature for basing thermal tunneling exclusion"
                   + " = "
                   + exclusionTemperatureString
                   + " GeV.\n\n" )
            thermalTunnelingSurvivalProbabilityString = str(
                                   vcs.ThermalTunnelingSurvivalProbability(
                                               optimalTunnelingTemperature,
                                                          thermalAction ) )


# Finally the output file is written:
outputText = ( "  <reference version=\"1.2.03\""
               + " citation=\"arXiv:1307.1477, arXiv:1405.7376 (hep-ph)\" />\n"
               + "  <stability slha_summary_code=\""
               + str( slhaSummaryCode )
               + "\" > "
               + metastabilityVerdict
               + " </stability>\n"
               + "  <quantum_stability> "
               + quantumStabilityVerdict
               + " </quantum_stability>\n"
               + "  <thermal_stability> "
               + thermalStabilityVerdict
               + " </thermal_stability>\n"
               + "  <panic_vacuum   relative_depth=\""
               + str( vcs.panicVacuum[ "PotentialValue" ] )
               + "\" "
               + VPD.UserFieldsAsXml( vcs.panicVacuum[ "FieldValues" ] )
               + " />\n  <global_minimum  relative_depth=\""
               + str( vcs.globalMinimum[ "PotentialValue" ] )
               + "\" "
               + VPD.UserFieldsAsXml( vcs.globalMinimum[ "FieldValues" ] )
               + " />\n  <DSB_vacuum   relative_depth=\""
               + str( vcs.dsbVacuum[ "PotentialValue" ] )
               + "\" "
               + VPD.UserFieldsAsXml( vcs.dsbVacuum[ "FieldValues" ] )
               + " />\n  <lifetime  action_calculation=\""
               + quantumTunnelingActionType
               + "\" > "
               + quantumTunnelingTimeInUniverseAgesString
               + " </lifetime>\n"
               + " <tunneling_temperature survival_probability=\""
               + thermalTunnelingSurvivalProbabilityString
               + "\" > "
               + exclusionTemperatureString
               + " </tunneling_temperature>" )
outputFile = open( VPD.outputFile, "w" )
outputFile.write( "<Vevacious_result>\n"
                  + outputText )# Each warning is printed as an XML element:
for warningMessage in vcs.warningMessages:
    outputFile.write( "\n  <warning>\n  "
                      + warningMessage
                      + "\n  </warning>" )
outputFile.write( "\n</Vevacious_result>\n" )
outputFile.close()
print( "Result summary (not recapping warnings):\n"       + outputText )
