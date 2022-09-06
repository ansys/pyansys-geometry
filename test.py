from scipy.integrate import quad

a, b = 2, 1


def integrand(theta, ecc):
    return (1 - ecc**2 * np.sin(theta) ** 2) ** 0.5


integrand = lambda theta: (1 - np.exp(2) * np.sin(theta) ** 2) ** 0.5
perimeter = 4 * a * quad(integrand, 0, np.pi / 2)
