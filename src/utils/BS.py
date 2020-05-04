import math
import scipy.stats as stats
import numpy

def N(x):
    return ((1.0/math.sqrt(2.0*math.pi)) * math.exp(-x*x*0.5))

def d1(S0, K, r, T, sigma, q):
    deno = (sigma * math.sqrt(T))
    if (deno==0):
        return 0
    logReturns = math.log(S0/float(K)) if ((S0/float(K)) > 0.0) else 0.0
    return (float(logReturns) + (float(r) - float(q) + float(sigma)*float(sigma)*0.5)*float(T)) / float(deno)
    
def d2(S0, K, r, T, sigma, q):
    return d1(S0, K, r, T, sigma, q)-sigma*math.sqrt(T)
        
def optionValueOfCall(S0, K, r, T, sigma, q):       
    _d1 = d1(S0, K, r, T, sigma, q)
    _d2 = d2(S0, K, r, T, sigma, q)
    return S0*math.exp(-q*T)*N(_d1)- K*math.exp(-r*T)*N(_d2)
      
def optionValueOfPut(S0, K, r, T, sigma, q):
    _d1 = d1(S0, K, r, T, sigma, q)
    _d2 = d2(S0, K, r, T, sigma, q)
    return float(K)*math.exp(-float(r)*float(T))*N(-_d2) - float(S0)*math.exp(-float(q)*float(T))*N(-_d1)
    
def delta(callput, S0, K, r, T, sigma, q):
    _d1 = d1(S0, K, r, T, sigma, q)        
    if callput.lower() == "call":            
        return N(_d1) * math.exp(-q*T)
    else:
        return (N(_d1)-1)* math.exp(-q*T)

def vega(S0, K, r, T, sigma, q):
    _d1 = d1(S0, K, r, T, sigma, q)
    return S0  * math.sqrt(T) * N(_d1)  * math.exp(-q*T)

def bsformula(callput, S0, K, r, T, sigma, q=0): 
    # callput(str): "call" or "put"
    # S0: underlying asset price
    # K: strike price
    # r: risk-free rate
    # T: year
    # sigma: stock price volatility
    if callput.lower()=="call":
        optionValue = optionValueOfCall(S0, K, r, T, sigma, q)
    else:
        optionValue = optionValueOfPut(S0, K, r, T, sigma, q)
        
    _delta = delta(callput, S0, K, r, T, sigma, q)
    _vega = vega(S0, K, r, T, sigma, q)
    
    return (optionValue, _delta, _vega)

if __name__ == "__main__":
    callput = "call"
    S0 = 2.85
    K = 2.40
    r = 0.02
    T = 180/365
    sigma = 0.2
    print(bsformula(callput, S0, K, r, T, sigma))