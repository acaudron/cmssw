import FWCore.ParameterSet.Config as cms

flavPlots = 'allbcldusg'
from DQMOffline.RecoB.bTagCommon_cff import *

ptJetRanges = (30,200,500,1500,5000)
ptLoop = [1]#[0,0.4,0.8,1,1.5,2]
nPixHitLoop = [0,1,2,3]
nHitLoop = [5,6,7,8,9]
chi2Loop = [5]
decLenLoop = [5]
distJetAxisLoop = [0.7]
SVptLoop = [0.8]
SVnHitLoop = nHitLoop

def newSelection(process,
                 postfix="",
                 minimumNumberOfPixelHits=2,
                 minimumNumberOfHits=8,
                 minimumTransverseMomentum=1.0,
                 maximumChiSquared=5.0,
                 maximumDecayLength=5.0,
                 maximumDistanceToJetAxis=0.07,
                 SVminimumNumberOfHits=8,
                 SVminimumTransverseMomentum=0.8
                 ):
    process.load("RecoBTag.Configuration.RecoBTag_cff")
    #update IPtagInfo
    setattr(process,
            "pfImpactParameterTagInfos"+postfix,
            process.pfImpactParameterTagInfos.clone(
              minimumNumberOfPixelHits = cms.int32(minimumNumberOfPixelHits),
              minimumNumberOfHits = cms.int32(minimumNumberOfHits),
              minimumTransverseMomentum=cms.double(minimumTransverseMomentum),
              maximumChiSquared = cms.double(maximumChiSquared)
              )
            )
    #update TC and JP computers
    computers = ["candidateTrackCounting3D2ndComputer","candidateTrackCounting3D3rdComputer","candidateJetProbabilityComputer","candidateJetBProbabilityComputer"]
    for computer in computers:
        setattr(process,
                computer+postfix,
                getattr(process,computer).clone(
                maximumDecayLength = cms.double(maximumDecayLength),
                maximumDistanceToJetAxis = cms.double(maximumDistanceToJetAxis),
                )
                )
    #update TC and JP taggers
    for i, tag in enumerate(["pfTrackCountingHighEffBJetTags", "pfTrackCountingHighPurBJetTags", "pfJetProbabilityBJetTags", "pfJetBProbabilityBJetTags"]):
        setattr(process,
                tag+postfix,
                getattr(process,tag).clone(
                tagInfos = cms.VInputTag(cms.InputTag("pfImpactParameterTagInfos"+postfix)),
                jetTagComputer = cms.string(computers[i])
                )
                )
    #update track selection PSet for CSV taggers
    process.load("RecoBTag.SecondaryVertex.combinedSecondaryVertexCommon_cff")
    setattr(process, "trackPseudoSelectionBlock"+postfix, process.trackPseudoSelectionBlock.clone())
    getattr(process, "trackPseudoSelectionBlock"+postfix).trackPseudoSelection.maxDecayLen = cms.double(maximumDecayLength)
    getattr(process, "trackPseudoSelectionBlock"+postfix).trackPseudoSelection.maxDistToAxis = cms.double(maximumDistanceToJetAxis)
    setattr(process, "trackSelectionBlock"+postfix, process.trackSelectionBlock.clone())
    getattr(process, "trackSelectionBlock"+postfix).trackSelection.maxDecayLen = cms.double(maximumDecayLength)
    getattr(process, "trackSelectionBlock"+postfix).trackSelection.maxDistToAxis = cms.double(maximumDistanceToJetAxis)
    setattr(process,
            "candidateCombinedSecondaryVertexV2Computer"+postfix,
            process.candidateCombinedSecondaryVertexV2Computer.clone(
                trackPseudoSelection = getattr(process, "trackPseudoSelectionBlock"+postfix).trackPseudoSelection,
                trackSelection = getattr(process, "trackSelectionBlock"+postfix).trackSelection
            )
            )
    #SV tracks/vertex chain
    setattr(process,
            "inclusiveCandidateVertexFinder"+postfix,
            process.inclusiveCandidateVertexFinder.clone(
            minHits = SVminimumNumberOfHits,
            minPt = SVminimumTransverseMomentum
            )
            )
    setattr(process,
            "candidateVertexMerger"+postfix,
            process.candidateVertexMerger.clone(secondaryVertices = cms.InputTag("inclusiveCandidateVertexFinder"+postfix))
            )
    setattr(process,
            "candidateVertexArbitrator"+postfix,
            process.candidateVertexArbitrator.clone(secondaryVertices = cms.InputTag("candidateVertexMerger"+postfix))
            )
    setattr(process,
            "inclusiveCandidateSecondaryVertices"+postfix,
            process.inclusiveCandidateSecondaryVertices.clone(secondaryVertices = cms.InputTag("candidateVertexArbitrator"+postfix))
            )
    setattr(process,
            "pfInclusiveSecondaryVertexFinderTagInfos"+postfix,
            process.pfInclusiveSecondaryVertexFinderTagInfos.clone(extSVCollection = cms.InputTag("inclusiveCandidateSecondaryVertices"+postfix))
            )
    #update CSVv2
    setattr(process,
            "pfCombinedInclusiveSecondaryVertexV2BJetTags"+postfix,
            process.pfCombinedInclusiveSecondaryVertexV2BJetTags.clone(
            tagInfos = cms.VInputTag(cms.InputTag("pfImpactParameterTagInfos"+postfix), cms.InputTag("pfInclusiveSecondaryVertexFinderTagInfos"+postfix)),
            jetTagComputer = cms.string("candidateCombinedSecondaryVertexV2Computer"+postfix)
            )
            )
    #sequence
    setattr(process,
            "pfBTagging"+postfix,
            cms.Sequence(
             getattr(process,"pfImpactParameterTagInfos"+postfix) *
             ( getattr(process,"pfTrackCountingHighEffBJetTags"+postfix) +
               getattr(process,"pfTrackCountingHighPurBJetTags"+postfix) +
               getattr(process,"pfJetProbabilityBJetTags"+postfix) +
               getattr(process,"pfJetBProbabilityBJetTags"+postfix) +
               getattr(process,"inclusiveCandidateVertexFinder"+postfix) *
               getattr(process,"candidateVertexMerger"+postfix) *
               getattr(process,"candidateVertexArbitrator"+postfix) *
               getattr(process,"inclusiveCandidateSecondaryVertices"+postfix) *
               getattr(process,"pfInclusiveSecondaryVertexFinderTagInfos"+postfix) *
               getattr(process,"pfCombinedInclusiveSecondaryVertexV2BJetTags"+postfix)
               )
             ))
    process.btagSequence = cms.Sequence(process.btagSequence+getattr(process,"pfBTagging"+postfix))

def newTagsDQM(postfix=""):
    adtionalTags = cms.VPSet(
        cms.PSet(
            bTagTrackCountingAnalysisBlock,
            label = cms.InputTag("pfTrackCountingHighEffBJetTags"+postfix),
            folder = cms.string("TCHE_"+postfix)
            ),
        cms.PSet(
            bTagTrackCountingAnalysisBlock,
            label = cms.InputTag("pfTrackCountingHighPurBJetTags"+postfix),
            folder = cms.string("TCHP_"+postfix)
            ),
        cms.PSet(
            bTagProbabilityAnalysisBlock,
            label = cms.InputTag("pfJetProbabilityBJetTags"+postfix),
            folder = cms.string("JP_"+postfix)
            ),
        cms.PSet(
            bTagBProbabilityAnalysisBlock,
            label = cms.InputTag("pfJetBProbabilityBJetTags"+postfix),
            folder = cms.string("JBP_"+postfix)
            ),
        cms.PSet(
            bTagGenericAnalysisBlock,
            label = cms.InputTag("pfCombinedInclusiveSecondaryVertexV2BJetTags"+postfix),
            folder = cms.string("CSVv2_"+postfix)
            ),
        cms.PSet(
            bTagTrackIPAnalysisBlock,
            type = cms.string('CandIP'),
            label = cms.InputTag("pfImpactParameterTagInfos"+postfix),
            folder = cms.string("IPTag"+postfix)
            ),
        cms.PSet(
            bTagCombinedSVAnalysisBlock,
            listTagInfos = cms.VInputTag(
                cms.InputTag("pfImpactParameterTagInfos"+postfix),
                cms.InputTag("pfInclusiveSecondaryVertexFinderTagInfos"+postfix)
                ),
            type = cms.string('GenericMVA'),
            label = cms.InputTag("candidateCombinedSecondaryVertexV2Computer"+postfix),
            folder = cms.string("CSVTag"+postfix)
            ),
    )
    return adtionalTags
