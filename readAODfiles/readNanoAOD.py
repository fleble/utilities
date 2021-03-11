from coffea.nanoevents import NanoEventsFactory, BaseSchema

fileName = "test.root"
events = NanoEventsFactory.from_root(fileName, schemaclass=BaseSchema).events()

nevt = len(events.FatJet_pt)

for ievt in range(nevt):
    njets = len(events.FatJet_pt[ievt])
    if njets > 3:
        print("\n%d jets in event %d:" %(njets, ievt))
        print("eta")
        for ijet in range(njets):
            print(events.FatJet_eta[ievt][ijet])
        print("phi")
        for ijet in range(njets):
            print(events.FatJet_phi[ievt][ijet])
        print("pt")
        for ijet in range(njets):
            print(events.FatJet_pt[ievt][ijet])
        print("mass")
        for ijet in range(njets):
            print(events.FatJet_mass[ievt][ijet])
    else:
        print("\n0 jet in event %d, skipping." %ievt)

