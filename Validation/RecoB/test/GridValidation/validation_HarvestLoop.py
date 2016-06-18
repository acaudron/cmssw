# The following comments couldn't be translated into the new config version:

#! /bin/env cmsRun

import FWCore.ParameterSet.Config as cms

runOnMC = True

process = cms.Process("harvest")
process.load("DQMServices.Components.DQMEnvironment_cfi")

#keep the logging output to a nice level
process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load("DQMServices.Core.DQM_cfg")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)
)
process.source = cms.Source("DQMRootSource",
    fileNames = cms.untracked.vstring()
)

process.load("Validation.RecoB.bTagAnalysis_harvesting_cfi")

#loading configuration from  trackOptimisation_cfi.py file
from Validation.RecoB.trackOptimisationLoop_cfi import *
tags = bTagCommonBlock.tagConfig
for pt in ptLoop:
    for nPixHit in nPixHitLoop:
        for nHit in nHitLoop:
            for chi2 in chi2Loop:
                for decLen in decLenLoop:
                    for distJetAxis in distJetAxisLoop:
                        for SVpt in SVptLoop:
                            for SVnHit in SVnHitLoop:
                                if not SVnHit==nHit : continue
                                postfix="ptMin"+str(pt).replace(".","d")+"nPixHitMin"+str(nPixHit)+"nHitMin"+str(nHit)+"chi2Max"+str(chi2).replace(".","d")+"decLenMax"+str(decLen).replace(".","d")+"distJAMax"+str(distJetAxis).replace(".","d")+"SVptMin"+str(SVpt).replace(".","d")+"SVnHitMin"+str(SVnHit)
                                tags += newTagsDQM(postfix=postfix)

process.bTagValidationHarvest.tagConfig = tags
process.bTagValidationHarvest.flavPlots = flavPlots
process.bTagValidationHarvest.ptRanges = cms.vdouble(ptJetRanges)

if runOnMC:
	process.dqmSeq = cms.Sequence(process.bTagValidationHarvest * process.dqmSaver)
else:
	process.dqmSeq = cms.Sequence(process.bTagValidationHarvestData * process.dqmSaver)

process.plots = cms.Path(process.dqmSeq)

process.dqmEnv.subSystemFolder = 'BTAG'
process.dqmSaver.producer = 'DQM'
process.dqmSaver.workflow = '/POG/BTAG/BJET'
process.dqmSaver.convention = 'Offline'
process.dqmSaver.saveByRun = cms.untracked.int32(-1)
process.dqmSaver.saveAtJobEnd =cms.untracked.bool(True) 
process.dqmSaver.forceRunNumber = cms.untracked.int32(1)

process.DQMRootSource.fileNames = [
    'file:MEtoEDMConverter.root'
]

