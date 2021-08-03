#!/usr/bin/env python3

import numpy as np
from gurobipy import *
import matplotlib.pyplot as plt
import time
import random

def testImport():
    print("Victory")
    return


def radialDistanceCompute(point, site):
    return point[0]*site[0] + point[1]*site[1]

def LSADistanceCompute(point1, point2):
    return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2

def nonWeightedDistanceLSA(sites, points):
    distance = np.zeros((len(sites), len(points)))

    for i in range(len(sites)):
        for j in range(len(points)):
            distance[i][j] = LSADistanceCompute(sites[i], points[j])
    return distance

def nonWeightedDistanceRadial(sites, points):
    distance = np.zeros((len(sites), len(points)))
    for i in range(len(sites)):
        for j in range(len(points)):
            distance[i][j] = radialDistanceCompute(points[j], sites[i])
    return distance

def genCurPointAssign(modVars,n,k):
    #if we make a version where n and k are global this can change, but for now we are passing numbers to this function
    assignVect = np.zeros(k)
    for i in range(n):
        for j in range(k):
            if modVars[k*i + j] == 1.0:
                assignVect[j] = i
    return assignVect

def sameAssignment(assignment1, assignment2):
    for i in range(len(assignment1)):
        if assignment1[i] == assignment2[i]:
            continue
        else:
            return False
    return True

#assignment 1 are length n. this has actual numbers in it for the clusters
def diffCounter(assignment1, assignment2):
    #print("length of assignment1", len(assignment1))
    count = 0
    for i in range(len(assignment1)):
        if assignment1[i] != assignment2[i]:
            count +=1
    return count

def genStepBounds(high, low, snap):
    highStep = np.zeros(len(high))
    lowStep = np.zeros(len(low))
    for i in range(len(high)):
        cnt = snap[i]
        if cnt > low[i] :
            lowStep[i] = cnt - 1
        else:
            lowStep[i] = low[i]

        if cnt < high[i]:
            highStep[i] = cnt + 1
        else:
            highStep[i] = high[i]

    return highStep, lowStep


#this creates a list of pairs (lost, anything) and (anything, grew)
def getWiderRangeOfChangedClusters(oldAssignCount,siteAssignCount,upper,lower): #returns list of tuples
    #print("oldAssignCount", oldAssignCount)
    #print("siteAssignCount", siteAssignCount)
    changed = []
    grew = []
    lost = []
    for i in range(len(siteAssignCount)):
        if siteAssignCount[i] - oldAssignCount[i] == 0:
            continue
        elif siteAssignCount[i] - oldAssignCount[i] < 0:
            lost.append(i)
        elif siteAssignCount[i] - oldAssignCount[i] > 0:
            grew.append(i)
    for i in range(len(lost)):
        for k in range(len(upper)):
            if oldAssignCount[k] < upper[k] and not k==i:
                changed.append((lost[i],k))
    for i in range(len(grew)):
        for k in range(len(lower)):
            if oldAssignCount[k] > lower[k] and not k==i:
                changed.append((k,grew[i]))
    return changed

def getAllPairsOfClusters(k,currentAssignCount,lower,upper): #returns list of tuples
    changed = []
    #print("current in all pairs", currentAssignCount)
    #print(lower)
    #print(upper)
    for i in range(k):
        for j in range(k):
            if currentAssignCount[i] > lower[i] and currentAssignCount[j] < upper[j] and not j==i:
                changed.append((i,j))
    #print("all allowable cluster pairs", changed)
    return changed



def sameAssignment(assignment1, assignment2):
    for i in range(len(assignment1)):
        if assignment1[i] == assignment2[i]:
            continue
        else:
            return False
    return True

def exchangeCount(oldAssignCount, siteAssignCount): # boolean
    added = 0
    #lost = 0
    for i in range(len(siteAssignCount)):
        if siteAssignCount[i] - oldAssignCount[i] == 0:
            continue
            #this worked with "lost" twice
        #elif siteAssignCount[i] - oldAssignCount[i] < 0:
        #    lost += siteAssignCount[i] - oldAssignCount[i]
        #only count those that are larger.
        elif siteAssignCount[i] - oldAssignCount[i] > 0:
            added += siteAssignCount[i] - oldAssignCount[i]
    #if added > 1:
    #    return added
    return added

#this creates a list of pairs (lost, grew)
def getChangedClusters(oldAssignCount,siteAssignCount): #returns list of tuples
    #print("oldAssignCount", oldAssignCount)
    #print("siteAssignCount", siteAssignCount)
    changed = []
    grew = []
    lost = []
    for i in range(len(siteAssignCount)):
        if siteAssignCount[i] - oldAssignCount[i] == 0:
            continue
        elif siteAssignCount[i] - oldAssignCount[i] < 0:
            lost.append(i)
        elif siteAssignCount[i] - oldAssignCount[i] > 0:
            grew.append(i)
    for i in range(len(lost)):
        for k in range(len(grew)):
            changed.append((lost[i],grew[k]))
    return changed



# there were multiple typos in here. means it was never used
def genLimitedBounds(index, oldassign):
    ubound = oldassign.tolist()
    lbound = oldassign.tolist()
    lbound[index[0]] = oldassign[index[0]] - 1
    ubound[index[1]] = oldassign[index[1]] + 1
    return ubound, lbound

def clusterInfeasible(uBound, lBound, assignCounts, assignVect):
    for i in range(len(assignCounts)):
        if assignCounts[i] > uBound[i] or assignCounts[i] < lBound[i]:
            return True
    for i in range(len(assignVect)):
        if assignVect[i] > 1.0 or assignVect[i] < 0.0:
            return True
    return False

def printCurrentAssignment( assign, points, sites):
    for i in range(len(points)):
        if assign[i] == 0:
            plt.plot(points[i][0],points[i][1], 'go')
        elif assign[i] == 1:
            plt.plot(points[i][0],points[i][1], 'bo')
        elif assign[i] == 2:
            plt.plot(points[i][0],points[i][1], 'ro')
        elif assign[i] == 3:
            plt.plot(points[i][0],points[i][1], 'co')
        else:
            plt.plot(points[i][0],points[i][1], 'mo')
    plt.plot(sites[0][0],sites[0][1], 'gx')
    plt.plot(sites[1][0],sites[1][1], 'bx')   
    plt.plot(sites[2][0],sites[2][1], 'rx')
    plt.plot(sites[3][0],sites[3][1], 'cx')
    plt.plot(sites[4][0],sites[4][1], 'mx')
    plt.show()
    return


def getCurrentSites(start, end, curLambda):
    tempSites = np.copy(start)
    for i in range(len(tempSites)):
        tempSites[i][0] = start[i][0] + float(curLambda)*(end[i][0] - start[i][0])
        tempSites[i][1] = start[i][1] + float(curLambda)*(end[i][1] - start[i][1])
    return tempSites

