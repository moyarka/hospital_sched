from random import choice, sample, random
from operator import itemgetter
import copy

testFile1 = "test1.txt"
testFile2 = "test2.txt"

def readInput(testFile) :
    file = open(testFile, 'r+')
    fileList = file.readlines()
    fileList = [s.replace('\n', '') for s in fileList]
    
    [days, doctors] = [int(i) for i in fileList[0].split()]
    maxCapacity = int(fileList[1])
    
    allShifts = []
    for i in range(2, days + 2):
        dayRequirements = fileList[i].split()
        morningReqs = [int(i) for i in dayRequirements[0].split(",")]
        eveningReqs = [int(i) for i in dayRequirements[1].split(",")]
        nightReqs = [int(i) for i in dayRequirements[2].split(",")]
        
        allShifts.append((morningReqs, eveningReqs, nightReqs))

    file.close()
    return [days, list(range(doctors)), maxCapacity, allShifts]

class JobScheduler:
    def __init__(self, fileInfo, fileIdx):
        self.fileIdx = fileIdx

        self.days = fileInfo[0]
        self.doctors = len(fileInfo[1])
        self.doctorsIds = fileInfo[1]
        self.maxCapacity = fileInfo[2]
        self.allShifts = fileInfo[3]

        self.popSize = 32
        self.chromosomes = self.generateInitialPopulation()
        self.crossOverPoints = max(self.days // 2, 3)
        self.elitismPercentage = 16
        self.pc = 0.65 # (crossover probability)
        self.pm = 0.02  # (mutation probability)
        
        self.bestFit = []

    def printChromosome(self, chromosome):
        for i in range(self.doctors):
            for j in range(self.days):
                print(chromosome[i][j], end=' ')
            print()
    
    def generateSingleChromosome(self):
        res = [['' for i in range(self.days)] for j in range(self.doctors)]
        for i in range(self.doctors):
            for j in range(self.days):
                res[i][j] = choice('meno')
        return res
    
    def generateInitialPopulation(self):
        res = []
        for i in range(self.popSize):
            res.append(self.generateSingleChromosome())
        return res
    
    def crossOver(self, par1, par2):
        selection = [0 for i in range(self.days)]
        points = sample(range(0, self.days - 1), self.crossOverPoints)

        for p in points:
            randNum = random()
            if randNum < self.pc:
                selection[p] = 1

        child = []
        
        for i in range(self.doctors):
            childRow = []
            for j in range(self.days):
                if selection[i] == 0:
                    childRow.append(par1[i][j])
                else:
                    childRow.append(par2[i][j])
            child.append(childRow)
        return child
        
    def mutateDay(self, daySched):
        res = ''
        randNum = random()
        if randNum < self.pm:
            res = choice('meno')
        else:
            res = daySched
        return res
    
    def mutate(self, chromosome):
        for i in range(self.doctors):
            for j in range(self.days):
                chromosome[i][j] = self.mutateDay(chromosome[i][j])
        return chromosome

    def countDoctors(self, chromosome, day, shift):
        res = 0
        for i in range(self.doctors):
            if chromosome[i][day] == shift:
                res += 1
        return res
    
    def calculateFitness(self, chromosome):
        mistakes = 0
        for i in range(self.doctors):
            for j in range(self.days - 1):
                if chromosome[i][j] == 'n' and chromosome[i][j + 1] in 'me':
                    mistakes += 1
        
        for i in range(self.doctors):
            for j in range(self.days - 2):
                if chromosome[i][j] == 'n' and chromosome[i][j+1] == 'n'\
                    and chromosome [i][j+2] == 'n':
                    mistakes += 1
        
        for i in range(self.days):
            dayDocs = self.countDoctors(chromosome, i, 'm')
            eveningDocs = self.countDoctors(chromosome, i, 'e')
            nightDocs = self.countDoctors(chromosome, i, 'n')
            
            if dayDocs < self.allShifts[i][0][0]:
                mistakes += 1
            if self.allShifts[i][0][1] < dayDocs:
                mistakes += 1
            if eveningDocs < self.allShifts[i][1][0]:
                mistakes += 1
            if self.allShifts[i][1][1] < eveningDocs:
                mistakes += 1
            if nightDocs < self.allShifts[i][2][0]:
                mistakes += 1
            if self.allShifts[i][2][1] < nightDocs:
                mistakes += 1
            
        for i in range(self.doctors):
            offDays = chromosome[i].count('o')
            if self.maxCapacity < (self.days - offDays):
                mistakes += 1
        
        return mistakes
        
    def generateNewPopulation(self, sortedFitnessVals):
        elitesCount = (self.popSize * self.elitismPercentage) // 100
        res = []
        
        matingPool = sortedFitnessVals[:max(elitesCount, 2)]
        for i in range(self.popSize - elitesCount):
            parents = sample(matingPool, 2)
            par1, par2 = parents[0][1], parents[1][1]
            newChild = self.crossOver(par1, par2)
            mutatedChild = self.mutate(newChild)
            res.append(mutatedChild)
            
        for par in matingPool:
            res.append(par[1])
        return res

    def writeAnswer(self):
        res = []
        for d in range(self.days):
            day = []
            for s in 'men':
                shift = []
                for doc in range(self.doctors):
                    if self.bestFit[doc][d] == s:
                        shift.append(doc)
                day.append(shift)
            res.append(day)

        fileName = 'output' + str(self.fileIdx) + '.txt'
        resFile = open(fileName, 'w')
        
        for day in res:
            dayStr = ''
            for shift in day:
                if len(shift) == 0:
                    dayStr += 'empty'
                else:
                    for i in range(len(shift) - 1):
                        dayStr += str(shift[i]) + ','
                    dayStr += str(shift[-1])
                dayStr += ' '
            print(dayStr)
            resFile.write(dayStr + '\n')
        resFile.close()

    def schedule(self): 
        for generation in range(100000):
            fitnessVals = []
            for chrom in self.chromosomes:
                chrFitness = self.calculateFitness(chrom)
                fitnessVals.append((chrFitness, chrom))

            sortedFitnessVals = sorted(fitnessVals, key=itemgetter(0))

            if sortedFitnessVals[0][0] == 0:
                print('best fit in generation {0}: {1}'.\
                    format(generation, sortedFitnessVals[0][0]))
                self.bestFit = sortedFitnessVals[0][1]
                break
            else:
                self.chromosomes = self.generateNewPopulation(sortedFitnessVals)
        
        return

import time

fileInfo1 = readInput(testFile1)

start = time.time()

scheduler = JobScheduler(fileInfo1, 1)
scheduler.schedule()

end = time.time()

print()
scheduler.printChromosome(scheduler.bestFit)
print()
scheduler.writeAnswer()
print()

print("test 1: ", '%.2f'%(end - start), 'sec')


print()
fileInfo2 = readInput(testFile1)

start = time.time()

scheduler = JobScheduler(fileInfo2, 2)
scheduler.schedule()

end = time.time()

print()
scheduler.printChromosome(scheduler.bestFit)
print()
scheduler.writeAnswer()
print()

print("test 2: ", '%.2f'%(end - start), 'sec')
