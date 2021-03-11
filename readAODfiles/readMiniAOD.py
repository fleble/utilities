import DataFormats.FWLite as fwlite
import numpy as np


## Open miniAOD
fileName = 'test.root'

events = fwlite.Events( fileName )

## Create handle outside of loop
handle = fwlite.Handle("vector<pat::Jet>")

## Collection label
label = ('slimmedJetsAK8')

## Loop over events
for ievt, event in enumerate(events):
    # If you just want to loop over a limited number of events
    #if ievt == 5: break

    # Example of code
    # Looking at AK8 jet pT for events having more than 4 AK8 jets with pT>170 GeV
    event.getByLabel(label, handle)
    jets = handle.product()
    njets = jets.size()
    pts = np.array([ jets[ijet].pt() for ijet in range(njets) ])
    nJetPtGt170 = np.sum(pts >= 170)
    
    if nJetPtGt170>3:
        print("\n%d jets in event %d" %(njets, ievt))
        for ijet in range(njets):
            print(jets[ijet].pt())

