# test push
# The following comments couldn't be translated into the new config version:
#! /bin/env cmsRun

import FWCore.ParameterSet.Config as cms
process = cms.Process("validation")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")

whichJets  = "ak4PFJetsCHS"
applyJEC = True
corrLabel = 'ak4PFCHSL1FastL2L3'
from Configuration.AlCa.GlobalTag import GlobalTag
tag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')
useTrigger = False
triggerPath = "HLT_PFJet80_v*"
runOnMC    = True
#Flavour plots for MC: "all" = plots for all jets ; "dusg" = plots for d, u, s, dus, g independently ; not mandatory and any combinations are possible                                     
#b, c, light (dusg), non-identified (NI), PU jets plots are always produced
flavPlots = "allbcldusg"

###prints###
print "jet collcetion asked : ", whichJets
print "JEC applied?", applyJEC, ", correction:", corrLabel 
print "trigger will be used ? : ", useTrigger, ", Trigger paths:", triggerPath
print "is it MC ? : ", runOnMC, ", Flavours:", flavPlots
print "Global Tag : ", tag
############

#loading configuration from  trackOptimisation_cfi.py file
from Validation.RecoB.trackOptimisationLoop_cfi import *

process.load("DQMServices.Components.DQMEnvironment_cfi")
process.load("DQMServices.Core.DQM_cfg")

process.load("JetMETCorrections.Configuration.JetCorrectors_cff")
process.load("CommonTools.ParticleFlow.goodOfflinePrimaryVertices_cfi")
process.load("RecoJets.JetAssociationProducers.ak4JTA_cff")
process.load("RecoBTag.Configuration.RecoBTag_cff")
process.load("PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi")
process.load("PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi")
process.load("PhysicsTools.JetMCAlgos.CaloJetsMCFlavour_cfi")

newjetID=cms.InputTag(whichJets)
process.ak4JetFlavourInfos.jets = newjetID
if not "ak4PFJetsCHS" in whichJets:
    process.ak4JetTracksAssociatorAtVertexPF.jets = newjetID
    process.pfImpactParameterTagInfos.jets        = newjetID
    process.softPFMuonsTagInfos.jets              = newjetID
    process.softPFElectronsTagInfos.jets          = newjetID
    process.patJetGenJetMatch.src                 = newjetID

	
#process.btagging = cms.Sequence(process.legacyBTagging + process.pfBTagging)
process.btagSequence = cms.Sequence(
    process.ak4JetTracksAssociatorAtVertexPF *
    process.pfBTagging *
    process.pfCTagging
    )
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
                                newSelection(process, postfix=postfix, minimumNumberOfPixelHits=nPixHit, minimumNumberOfHits=nHit, minimumTransverseMomentum=pt, maximumChiSquared=chi2, maximumDecayLength=decLen,maximumDistanceToJetAxis=distJetAxis,SVminimumNumberOfHits=SVnHit,SVminimumTransverseMomentum=SVpt)
                                tags += newTagsDQM(postfix=postfix)
                        
process.jetSequences = cms.Sequence(process.ak4PFCHSL1FastjetCorrector * process.ak4PFCHSL2RelativeCorrector * process.ak4PFCHSL3AbsoluteCorrector * process.ak4PFCHSL1FastL2L3Corrector * process.goodOfflinePrimaryVertices * process.btagSequence)

###
print "inputTag : ", process.ak4JetTracksAssociatorAtVertexPF.jets
###


process.load("Validation.RecoB.bTagAnalysis_firststep_cfi")
if runOnMC:
    process.flavourSeq = cms.Sequence(
        process.selectedHadronsAndPartons *
        process.ak4JetFlavourInfos
        )
    process.bTagValidationFirstStep.tagConfig = tags	
    process.bTagValidationFirstStep.ptRanges = cms.vdouble(ptJetRanges)	
    process.bTagValidationFirstStep.jetMCSrc = 'ak4JetFlavourInfos'
    process.bTagValidationFirstStep.applyPtHatWeight = False
    process.bTagValidationFirstStep.doJetID = True
    process.bTagValidationFirstStep.doJEC = applyJEC
    process.bTagValidationFirstStep.JECsource = cms.string(corrLabel)
    process.bTagValidationFirstStep.flavPlots = flavPlots
    #process.bTagValidationFirstStep.ptRecJetMin = cms.double(20.)
    process.bTagValidationFirstStep.genJetsMatched = cms.InputTag("patJetGenJetMatch")
    process.bTagValidationFirstStep.doPUid = cms.bool(True)
    process.ak4GenJetsForPUid = cms.EDFilter("GenJetSelector",
                                             src = cms.InputTag("ak4GenJets"),
                                             cut = cms.string('pt > 8.'),
                                             filter = cms.bool(False)
                                             )
    process.load("PhysicsTools.PatAlgos.mcMatchLayer0.jetMatch_cfi")
    process.patJetGenJetMatch.matched = cms.InputTag("ak4GenJetsForPUid")
    process.patJetGenJetMatch.maxDeltaR = cms.double(0.25)
    process.patJetGenJetMatch.resolveAmbiguities = cms.bool(True)
else:
    process.bTagValidationFirstStepData.doJEC = applyJEC
    process.bTagValidationFirstStepData.JECsource = cms.string(corrLabel)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

### Should help to avoid 8001 error 
#process.options = cms.untracked.PSet(
#SkipEvent = cms.untracked.vstring('ProductNotFound')
#)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring()
)

process.EDM = cms.OutputModule("DQMRootOutputModule",
                               outputCommands = cms.untracked.vstring('drop *',
                                                                      "keep *_MEtoEDMConverter_*_*"),
                               fileName = cms.untracked.string('MEtoEDMConverter.root')
                               )
from HLTrigger.HLTfilters.hltHighLevel_cfi import *
if useTrigger: 
    process.bTagHLT  = hltHighLevel.clone(TriggerResultsTag = "TriggerResults::HLT", HLTPaths = ["HLT_PFJet40_v*"])
    process.bTagHLT.HLTPaths = [triggerPath]

if runOnMC:
    process.dqmSeq = cms.Sequence(process.ak4GenJetsForPUid * process.patJetGenJetMatch * process.flavourSeq * process.bTagValidationFirstStep)
else:
    process.dqmSeq = cms.Sequence(process.bTagValidationFirstStepData)

if useTrigger:
    process.plots = cms.Path(process.bTagHLT * process.jetSequences * process.dqmSeq)
else:
    process.plots = cms.Path(process.jetSequences * process.dqmSeq)
    
process.outpath = cms.EndPath(process.EDM)

process.dqmEnv.subSystemFolder = 'BTAG'
process.dqmSaver.producer = 'DQM'
process.dqmSaver.workflow = '/POG/BTAG/BJET'
process.dqmSaver.convention = 'Offline'
process.dqmSaver.saveByRun = cms.untracked.int32(-1)
process.dqmSaver.saveAtJobEnd =cms.untracked.bool(True) 
process.dqmSaver.forceRunNumber = cms.untracked.int32(1)
process.PoolSource.fileNames = [
#    '/store/mc/RunIISpring16DR80/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/00000/02526A31-E605-E611-B4CF-001E67F3332A.root'
    '/store/mc/RunIISpring16DR80/QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8/AODSIM/PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/00000/00F411E4-E105-E611-A3F5-001E675A6AA9.root'
]

#keep the logging output to a nice level
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

# load the full reconstraction configuration, to make sure we're getting all needed dependencies
process.GlobalTag = tag

