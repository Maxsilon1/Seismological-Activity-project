import numpy as np
import matplotlib.pyplot as plt

def generate_signal(N):
    t = np.arange(N)
    signal = np.sin(2 * np.pi * t / N) + 0.5 * np.sin(8 * np.pi * t / N)
    return signal

# O(N^2)
def DFT(f):
    N = len(f)
    F = np.zeros(N, dtype=complex)
    for n in range(N):
        for k in range(N):
            exponent = -2j * np.pi * n * k / N
            F[n] += f[k] * np.exp(exponent)
    return F

def FFT(f, inverse=False):
    N = len(f)

    if N <= 1:
        return f

    even = FFT(f[0::2], inverse)
    odd  = FFT(f[1::2], inverse)

    sign = 1j if inverse else -1j

    F = np.zeros(N, dtype=complex)
    for k in range(N // 2):
        W = np.exp(2 * sign * np.pi * k / N)
        T = W * odd[k]
        F[k] = even[k] + T
        F[k + N // 2] = even[k] - T
    return F

def IFFT(F):
    N = len(F)
    result = FFT(F, True)
    return result / N

def Filtr(F_spectrum, a, b):
    N = len(F_spectrum)
    filtered = F_spectrum.copy()
    
    for k in range(N):
        freq_idx = k if k <= N // 2 else N - k
        if not (a <= freq_idx <= b):
            filtered[k] = 0j
    return filtered

def main():
    N = 128 

    a = int(input("Левая граница спектра: "))
    b = int(input("Правая граница спектра: "))

    signal = generate_signal(N)

    result_dft = DFT(signal)
    result_fft = FFT(signal)

    filtered_spectrum = Filtr(result_fft, a, b)

    filtered_signal = IFFT(filtered_spectrum).real

    print("\n--- Результаты (первые 4 значения) ---")
    print("DFT:", np.round(result_dft[:4], 2))
    print("FFT:", np.round(result_fft[:4], 2))

    t = np.arange(N)
    plt.figure(figsize=(10, 4))
    plt.plot(t, signal, label='Исходный')
    plt.plot(t, filtered_signal, label='После фильтра', linestyle='--')
    plt.legend()
    plt.xlabel("n")
    plt.ylabel("x[n]")
    plt.grid(True)
    plt.show()

main()