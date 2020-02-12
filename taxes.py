# FEDERAL TAX RATES FOR CANADA
#
# 2008 2009 https://www.taxtips.ca/priortaxrates/taxrates2009_2008.htm
# 2010 2011 https://www.taxtips.ca/priortaxrates/taxrates2010_2011/canada.htm
# 2011 2012 https://www.taxtips.ca/priortaxrates/tax-rates-2011-2012/canada.htm
# 2013 2014 https://www.taxtips.ca/priortaxrates/tax-rates-2013-2014/canada.htm
# 2015 2016 https://www.taxtips.ca/priortaxrates/tax-rates-2015-2016/canada.htm
# 2017 2018 https://www.taxtips.ca/priortaxrates/tax-rates-2017-2018/canada.htm
# 2019 2020 https://www.taxtips.ca/taxrates/canada.htm
#
# PROVINCIAL TAX RATES FOR ONTARIO
#
# 2008 2009 https://www.taxtips.ca/priortaxrates/taxrates2009_2008.htm#ON
# 2010 2011 https://www.taxtips.ca/priortaxrates/taxrates2010_2011/on.htm
# 2012 2013 https://www.taxtips.ca/priortaxrates/tax-rates-2012-2013/on.htm
# 2014 2015 https://www.taxtips.ca/priortaxrates/tax-rates-2014-2015/on.htm
# 2016 2017 https://www.taxtips.ca/priortaxrates/tax-rates-2016-2017/on.htm
# 2018 2019 https://www.taxtips.ca/priortaxrates/tax-rates-2018-2019/on.htm
#
# BASIC PERSONAL TAX CREDIT AMOUNTS also appear at 
#
# https://www.taxtips.ca/nrcredits/nrcredits2012base.htm
# https://www.taxtips.ca/nrcredits/tax-credits-2013-base.htm 

from math import fabs
import pandas as pd
import numpy as np

rent = { 2010 }  # years on which ON479 includes occupancy cost as a tax credit

# CSV necessary columns:
#
# T4 = Year, Income_box14, Deducted_box22, ECPP_box16, Pensionable_box26, EI_box18, RPP_box20, Adjustment_box52
# T4RSP = Year, Payments_box22, Deducted_box30
# Deductions = Year, Medical, Rent

T4 = pd.read_csv('T4.csv')
T4RSP = pd.read_csv('T4RSP.csv')
Deductions = pd.read_csv('Deductions.csv') 
y1 = set(T4['Year'].unique())
y2 = set(T4RSP['Year'].unique())
y3 = set(Deductions['Year'].unique())
span = sorted(list(y1 | y2 | y3))

credits = {
    'federal': {
        2008: 15.0
    },
    'provincial': {
        2008: 6.05,
        2010: 5.05
    }
}

incomeTaxRate = {
    'federal': {
        2008: [15.0, 22.0, 26.0, 29.0, 33.0],
        2016: [15.0, 20.5, 26.0, 29.0, 33.0] 
    },
    'provincial': {
        2008: [5.05, 9.15, 11.16], 
        2012: [5.05, 9.15, 11.16, 12.16],
        2013: [5.05, 9.15, 11.16, 13.16],
        2014: [5.05, 9.15, 11.16, 12.16, 13.16]
    }
}

cppMax = {
    2010: 2163.15
}

eiMax = {
    2010: 747.36
}

# Canada Employment Amount
CEA = {
    2010: 1051,
    2011: 1065,
    2012: 1095,
    2013: 1117,
    2014: 1127,
    2015: 1146,
    2016: 1161,
    2017: 1178,
    2018: 1195
}

dividends = {
    'eligible': {
        2008: [-5.75, 4.40, 10.20, 14.55],
        2010: [-4.28, 5.80, 11.56, 15.88],
        2011: [-2.02, 7.85, 13.49, 17.72],
        2012: [-0.03, 9.63, 15.15, 19.29],
        2016: [-0.03, 9.63, 15.15, 19.29, 24.81]
    },
    'nonElegible': { # a.k.a. small business / ineligible
        2008: [2.08, 10.83, 15.83, 19.58],
        2015: [4.70, 12.96, 17.68, 21.22],
        2016: [5.24, 11.67, 18.11, 21.62, 26.30],
        2018: [5.76, 12.14, 18.52, 22.00, 26.64],
        2019: [6.87, 13.19, 19.52, 22.97, 27.57]
    }
}

capitalGains = {
    2008: [7.5, 11.0, 13.0, 14.5],
    2016: [7.5, 11.0, 13.0, 14.5, 16.5]    
}

# Provincial Surtax Rate
surtaxRate = {
    2008: [0.20, 0.36]
}

# Federal Personal Income Tax 
federal = {
    'medical': {
        2010: (0.03, 2024),
        2011: (0.03, 2052),
        2012: (0.03, 2109),
        2013: (0.03, 2152),
        2014: (0.03, 2171),
        2015: (0.03, 2208),
        2016: (0.03, 2237),
        2017: (0.03, 2268),
        2018: (0.03, 2302)
    },
    'brackets': {
        2008: [37885, 75569, 123184],
        2009: [40726, 81452, 126264],
        2010: [40970, 81941, 127021],
        2011: [41544, 83088, 128800],
        2012: [42707, 85414, 132406],
        2013: [43561, 87123, 135054],
        2014: [43953, 87907, 136270],
        2015: [44701, 89401, 138586],
        2016: [45282, 90563, 140388, 200000],
        2017: [45916, 91831, 142353, 202800],
        2018: [46605, 93208, 144489, 205842],
        2019: [47630, 95259, 147667, 210371]},
    'basicPersonalTaxCredit': {
        2008: 9600,
        2009: 10320,
        2010: 10382, 
        2011: 10527,
        2012: 10822,
        2013: 11038,
        2014: 11138,
        2015: 11327,
        2016: 11474,
        2017: 11635,
        2018: 11809,
        2019: 12069,
        2020: 13299
    }
}

# Provincial Personal Income Tax
provincial = {
    'medical': {
        2010: (0.03, 2024),
        2011: (0.03, 2061),
        2012: (0.03, 2128),
        2013: (0.03, 2167),
        2014: (0.03, 2188),
        2015: (0.03, 2232),
        2016: (0.03, 2266),
        2017: (0.03, 2302),
        2018: (0.03, 2343)
    },    
    'brackets': {
        2009: [36848, 73698],
        2010: [37106, 74214],
        2011: [37774, 75550],
        2012: [39020, 78043, 500000],
        2013: [39723, 79448, 509000],
        2014: [40120, 80242, 150000, 220000],
        2015: [40922, 81847, 150000, 220000],
        2016: [41536, 83075, 150000, 220000],
        2017: [42201, 84404, 150000, 220000],
        2018: [42960, 85923, 150000, 220000],
        2019: [43906, 87813, 150000, 220000]
    },
    'surtax': {
        2008: [4162, 5249],
        2009: [4257, 5370],
        2010: [4006, 5127],
        2011: [4087, 5219],
        2012: [4213, 5392],
        2013: [4289, 5489],
        2014: [4331, 5543],
        2015: [4418, 5654],
        2016: [4484, 5739],
        2017: [4556, 5831],
        2018: [4638, 5936],
        2019: [4740, 6067]
    },
    'basicPersonalTaxCredit': {
        2008: 8681,
        2009: 8881,
        2010: 8943,
        2011: 9104,
        2012: 9405,
        2013: 9574,
        2014: 9670,
        2015: 9863,
        2016: 10011,
        2017: 10171 ,
        2018: 10354,
        2019: 10582,
        2020: 10783
    },
    'basicReduction': {
        2010: 206,
        2011: 210,
        2012: 217,
        2013: 221,
        2014: 223,
        2015: 228,
        2016: 231,
        2017: 235,
        2018: 239
    }
}

info = {'federal': federal,
        'provincial': provincial}

# probably varies by year, need to check
healthPremium = [(20000, 0.06, 0), 
                 (25000, 0, 300),
                 (36000, 0.06, 300),
                 (38500, 0, 450),
                 (48000, 0.25, 450),
                 (48600, 0, 600),
                 (72000, 0.25, 600),
                 (72600, 0, 750),
                 (200000, 0.25, 750),
                 (None, 0, 900)]

def getSurtax(tax, year):
    surtax = 0
    bracket = match(provincial['surtax'], year)
    rate = match(surtaxRate, year)
    for pos in range(len(bracket)):
        limit = bracket[pos]
        if tax > limit:
            taxable = tax - limit
            r = rate[pos]
            contrib = taxable * r
            surtax += contrib
            print('\t', year, '{:.4f} {:.2f} {:.2f}'.format(r, taxable, contrib))
        else:
            break
    return surtax

def getProvincialHealthPremium(income):
    for (limit, perc, lump) in healthPremium:
        if limit is None:
            return lump
        elif income < limit:
            return lump + max(income - limit, 0) * perc

def match(data, year):
    while year not in data:
        year -= 1
    return data[year]

def getTax(kind, year, income):
    bracket = match(info[kind]['brackets'], year)
    rate = match(incomeTaxRate[kind], year)
    tax = 0
    applied = 0
    for pos in range(len(bracket)):
        limit = bracket[pos]
        r = rate[pos] / 100.0
        taxable = min(income, limit) - applied
        contrib = round(r * taxable)
        if contrib > 0:
            print('\t', kind, year, '{:.4f} {:.2f} {:.2f}'.format(r, taxable, contrib))
        tax += contrib
        applied += taxable
    return tax

def getPersonalTaxCredit(year, kind, add):
    amount = info[kind]['basicPersonalTaxCredit'][year]
    data = bpa[kind]
    while year not in data:
        year -= 1
    rate = data[year] / 100
    return rate * amount + add

def test(): # verifications
    for kind in info:
        data = info[kind]
        for year in span:
            assert data['basicPersonalTaxCredit'][year] > data['basicPersonalTaxCredit'].get(year - 1, 0)
            assert data['basicPersonalTaxCredit'][year] < data['basicPersonalTaxCredit'].get(year + 1, 100) 
            prev = 0
            for (start, end, rate) in data['rates'][year]:
                print(year, prev, start, end)
                assert start == prev
                prev = end
    for income in range(10000, 250000, 10000):
        print(income, getProvincialHealthTax(income)) # this makes no sense yet

# IMPORTANT NOTE: this calculator does NOT contemplate
# self-employment, capital gains or dividends at present

def process(year):
    print('\nTAX CALCULATIONS FOR YEAR ', year, '\n') # separator
    vT4 = T4.loc[T4['Year'] == year]
    vT4RSP = T4RSP.loc[T4RSP['Year'] == year]
    vD = Deductions.loc[Deductions['Year'] == year]
    employmentIncome = vT4['Income_box14'].sum()
    incomeRRSP = vT4RSP['Payments_box22'].sum()
    commissions = vT4['Commissions_box42'].sum()
    totalIncome = employmentIncome + incomeRRSP 
    if totalIncome == 0:
        print(year, 'Incomplete data, postponing processing until all data is accounted for')
        return 0
    # FEDERAL TAX
    # T1
    print(year, 'T1, line 101: Employment income (box 14 in T4) = {:.2f}'.format(employmentIncome))
    if commissions > 0:
        print(year, 'T1, line 102: Commissions (box 42 in T4) = {:.2f}'.format(commissions))
    if incomeRRSP > 0:
        print(year, 'T1, line 129: RRSP income (box 22 in T4RSP) = {:.2f}'.format(incomeRRSP))
    print(year, 'T1, line 150: Total income = {:.2f}'.format(totalIncome))
    adjustment = vT4['Adjustment_box52'].sum() 
    print(year, 'T1, line 206: Pension adjustment (box 52 in T4) = {:.2f}'.format(adjustment))
    RRSP = vT4['RPP_box20'].sum() 
    print(year, 'T1, line 207: Registered pension plan deduction (box 20 in T4) =', RRSP)
    taxableIncome = totalIncome - RRSP
    print(year, 'T1, line 236: Taxable income = {:.2f}'.format(taxableIncome))    
    print(year, 'SCHEDULE 1, Step 1 / A')
    fbpa = federal['basicPersonalTaxCredit'][year]
    print(year, 'Schedule 1, line 300: Basic personal amount =', '{:.2f}'.format(fbpa))
    ECPP = min(vT4['ECPP_box16'].sum(), match(cppMax, year)) 
    print(year, 'Schedule 1, line 308: CPP contributions (box 16 in T4) =', '{:.2f}'.format(ECPP))
    EI = min(vT4['EI_box18'].sum(), match(eiMax, year)) 
    print(year, 'Schedule 1, line 312: Employment insurance premiums (box 18 in T4) =', EI)
    empl = min(match(CEA, year), taxableIncome)
    print(year, 'Schedule 1, line 363: Canada employment amount =', empl)
    (perc, amount) = match(federal['medical'], year)
    medicalLimit = min(perc * taxableIncome, amount)
    medicalExpenses = vD['Medical'].sum()
    print(year, 'Schedule 1, line 330.1: Medical expenses (reported total) =', '{:.2f}'.format(medicalExpenses))
    print(year, 'Schedule 1, line 330.2: Medical expenses (minimum to claim) =', '{:.2f}'.format(medicalLimit))
    medicalClaimed = max(0, medicalExpenses - medicalLimit) 
    print(year, 'Schedule 1, line 330.A: Medical expenses (claimed) =', '{:.2f}'.format(medicalClaimed))    
    schedule1step1 = fbpa + ECPP + EI + empl + medicalClaimed # line 25
    print(year, 'Schedule 1, line 27: Subtotal of federal deductions =', '{:.2f}'.format(schedule1step1))     
    rate = match(credits['federal'], year) 
    federalTaxCredits = (rate / 100.0) * schedule1step1
    # gifts and donations would be inserted at this point
    print(year,
          'Schedule 1, line 31: Tax credits at {:.0f}% rate = {:.2f}'.format(rate,
                                                                                            federalTaxCredits))
    print(year, 'SCHEDULE 1, Step 2 / B+C')    
    print(year, 'Schedule 1, line 32: COMPUTING FEDERAL TAX on', '{:.2f}'.format(taxableIncome))
    federalIncomeTax = getTax('federal', year, taxableIncome) 
    line = {2010: 's 37 & 39', 2011: 's 39 & 40', 2014: 's 46 & 49', 2015: 's 43 & 44'}
    print(year,
          'Schedule 1, line{:s}: Total federal tax on taxable income = {:.2f}'.format(match(line, year),
                                                                                      federalIncomeTax)) 
    basicFederalTax = max(0, federalIncomeTax - federalTaxCredits) # line 44
    line = {2010: '44', 2011: '48'}
    print(year, 'Schedule 1, line {:s}: Basic federal tax = {:.2f}'.format(match(line, year),
                                                                           basicFederalTax))
    pbpa = provincial['basicPersonalTaxCredit'][year]
    print(year, 'FORM ON428')
    print(year, 'ON428, line 1: Basic personal amount =', '{:.2f}'.format(pbpa))
    print(year, 'ON428, line 6: CPP contributions (same as in T1) =', '{:.2f}'.format(ECPP))
    print(year, 'ON428, line 8: EI premiums (same as in T1) =', EI)
    (perc, amount) = match(provincial['medical'], year)
    medicalLimit = min(perc * taxableIncome, amount)
    print(year, 'ON428, line 19: Medical expenses (reported total) =', '{:.2f}'.format(medicalExpenses))
    print(year, 'ON428, line 20: Medical expenses (minimum to claim) =', '{:.2f}'.format(medicalLimit))
    medicalClaimed = max(0, medicalExpenses - medicalLimit) 
    print(year, 'ON428, line 21: Medical expenses (claimed) =', '{:.2f}'.format(medicalClaimed))    
    form428step1 = pbpa + ECPP + EI + medicalClaimed
    print(year, 'ON428, line 24: Subtotal of provincial deductions =', '{:.2f}'.format(form428step1))         
    rate = match(credits['provincial'], year)
    provincialTaxCredits =  (rate / 100.0) * form428step1
    print(year,
          'ON428, line 26: Tax credits at rate {:.2f}% = {:.2f}'.format(rate,
                                                                                       provincialTaxCredits))
    # gifts and donations would be inserted at this point
    print(year, 'ON428, line 31: COMPUTING PROVINCIAL TAX on', '{:.2f}'.format(taxableIncome))
    provincialIncomeTax = getTax('provincial', year, taxableIncome)
    lines = {2010: '37 & 39', 2011: '38 & 39'}
    print(year, 'ON428, lines {:s}: Total provincial income tax = {:.2f}'.format(match(lines, year),
                                                                                 provincialIncomeTax))
    provincialIncomeTax -= provincialTaxCredits
    provincialIncomeTax = max(0, provincialIncomeTax)
    print(year, 'ON428, line 47: Provincial tax after credits =', '{:.2f}'.format(provincialIncomeTax))
    print(year, 'ON428, line 31: COMPUTING SURTAX on {:.2f}'.format(provincialIncomeTax))
    surtax = getSurtax(provincialIncomeTax, year)
    print(year, 'ON428, line 52: Surtax =', '{:.2f}'.format(surtax))
    provincialTax = provincialIncomeTax + surtax
    print(year, 'ON428, line 53: Gross provincial tax =', '{:.2f}'.format(provincialTax))
    basicReduction = match(provincial['basicReduction'], year)
    print(year, 'ON428, line 54 & 57: Basic reduction =', '{:.2f}'.format(basicReduction))
    reduction = 2 * basicReduction
    print(year, 'ON428, line 58 =', '{:.2f}'.format(reduction))    
    claimedReduction = max(0, 2 * reduction - provincialTax)
    print(year, 'ON428, line 54 & 60: Claimed reduction =', '{:.2f}'.format(claimedReduction))
    provincialTax -= claimedReduction
    provincialTax = max(0, provincialTax)
    print(year, 'ON428, lines 61 & 62: Reduced provincial tax =', '{:.2f}'.format(provincialTax))
    print(year, 'ON428, auxiliary form: COMPUTING ONTARIO HEALTH PREMIUM on', '{:.2f}'.format(taxableIncome))    
    healthPremium = getProvincialHealthPremium(taxableIncome) # auxiliary form on the ON428
    print(year, 'ON428, line 60: Health premium', '{:.2f}'.format(healthPremium)) 
    provincialTax += healthPremium # line 70
    print(year, 'ON428, line 70: Net provincial tax', '{:.2f}'.format(provincialTax))
    if year in rent:
        print(year, 'FORM ON479')        
        occupancyCost = vD['Rent'].sum() * 0.20 
        print(year, 'ON479, line 2: Gross occupancy cost', '{:.2f}'.format(occupancyCost)) 
        offset = 0.02 * (taxableIncome - 20000) # line 20
        occupancyCost -= offset
        print(year, 'ON470, line 21: Net occupancy cost', '{:.2f}'.format(occupancyCost)) 
    # back to T1
    totalPayable = basicFederalTax + provincialTax
    print(year, 'T1, line 435: Total payable tax', '{:.2f}'.format(totalPayable)) 
    # box 22 of T4 and box 30 of T4RSP
    deducted = vT4['Deducted_box22'].sum() + vT4RSP['Deducted_box30'].sum() 
    print(year, 'T1, line 437: Total income tax deducted (box 22 in T4) {:.2f}'.format(deducted))
    totalCredits = deducted
    if year in rent:
        totalCredits += occupancyCost
    print(year, 'T1, line 482: Total credits', '{:.2f}'.format(totalCredits)) 
    balance = totalPayable - totalCredits 
    print(year, 'T1, line 484: Balance', '{:.2f}'.format(balance)) 
    return balance

balance = 0
penalties = False
penalty = 0.05 + 12 * 0.01 # a full year late
for year in span:
    difference = round(process(year))
    if difference < 0 and penalties == True:
        difference -= penalty * difference 
    balance += difference
b = round(balance)
outcome = 'in favor' if b < 0 else 'owed'
if penalties:
    outcome += ' (including estimated penalties)'
print('\nSUMMARY\n\nTotal balance', '{:.2f}'.format(b), outcome)
                                                                               
