import pkg_resources
  
# Define white and blue color
white  = "\033[0;0m"
bold   = "\033[1m"
color1 =  "\033[48;5;17;38;5;251m"
color2 =  "\033[48;5;233;38;5;251m"

# Get list of packages with their version
installed_packages = sorted([(d.project_name, d.version) for d in pkg_resources.working_set], key=lambda x:x[0])

# Width of package name column in number of tabs
Ntabs = 1 + max([len(x[0]) for x in installed_packages])//8
maxLenVersion = max([len(x[1]) for x in installed_packages])

# Print header
col1name = "  Package name"
col2name = "Version"
ntabs = max(0, Ntabs-(len(col1name))//8)
print("")
print("%s%s%s%s%s" %(bold, col1name, ntabs*"\t", col2name, white))
print("-"*(Ntabs+2)*8)

# Print package name and version
for idx, (pkg, version) in enumerate(installed_packages):
    nspaces1 = max(0, 8*Ntabs-(len(pkg)+2))
    nspaces2 = maxLenVersion - len(version)
    # Alternate colors every two lines for legibility
    if idx%2 == 0: color = color1
    else:          color = color2
    print("%s  %s%s%s%s%s" %(color, pkg, nspaces1*" ", version, nspaces2*" ", white))

print("\nFound %d installed packages" %(len(installed_packages)))

