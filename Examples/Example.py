import pylab as plt
from AndorSifReader import AndorSifFile

if __name__ == "__main__":
    # Read file
    sif = AndorSifFile(r"led spectrum.sif")
    
    # Print properties
    print("\n".join(["%s: %s" % (k, v) for k, v in sif.signal.props.items()]))
    
    # Plot LED spectrum
    plt.figure(figsize = (12, 6))
    
    plt.subplot(121)
    plt.plot(1e9 * sif.signal.wls, sif.signal.data)
    plt.title("Signal")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Signal (a.u)")
    
    plt.subplot(122)
    plt.plot(1e9 * sif.bg.wls, sif.bg.data)
    plt.title("Background")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Signal (a.u)")
    
    plt.tight_layout()
    plt.show()