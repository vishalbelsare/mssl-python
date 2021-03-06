#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 10:42:16 2018

@author: goncalves1
"""
import pickle
import numpy as np
import scipy.optimize as spo
#import scipy.special


def logloss(w, x, y, Omega, lambda_reg):
    ''' MSSL with logloss function '''
    ntasks = Omega.shape[1]
    ndimension = int(len(w)/ntasks)
    wmat = np.reshape(w, (ndimension, ntasks), order='F')

    # make sure the data is in the correct format
    for t in range(ntasks):
        if len(y[t].shape) > 1:
            y[t] = np.squeeze(y[t])

    # cost function for each task
    cost = 0
    for t in range(ntasks):
        h_t_x = sigmoid(np.dot(x[t], wmat[:, t]))
#       h_t_x = scipy.special.expit(np.dot(x[t], wmat[:, t]))
        f1 = np.multiply(y[t], np.log(h_t_x))
        f2 = np.multiply(1-y[t], np.log(1-h_t_x))
        cost += -(f1 + f2).mean()

    # gradient of regularization term
    cost += (0.5*lambda_reg) * np.trace(np.dot(np.dot(wmat, Omega), wmat.T))
    return cost

def logloss_der(w, x, y, Omega, lambda_reg):
    ''' Gradient of the MSSL with logloss function '''

    ntasks = Omega.shape[1]
    ndimension = int(len(w)/ntasks)
    wmat = np.reshape(w, (ndimension, ntasks), order='F')

    # make sure data is in correct format
    for t in range(ntasks):
        if len(y[t].shape) > 1:
            y[t] = np.squeeze(y[t])

    # gradient of logloss term
    grad = np.zeros(wmat.shape)
    for t in range(ntasks):
#        sig_s = scipy.special.expit(np.dot(x[t], wmat[:, t])) #[:, np.newaxis]
        sig_s = sigmoid(np.dot(x[t], wmat[:, t]))
        grad[:, t] = np.dot(x[t].T, (sig_s-y[t]))/x[t].shape[0]
    # gradient of regularization term
    grad += lambda_reg * np.dot(wmat, Omega)
    grad = np.reshape(grad, (ndimension*ntasks, ), order='F')
    return grad

def sigmoid(a):
    # Logit function for logistic regression
    # x: data point (array or a matrix of floats)
    # w: set of weights (array of float)

    # treating over/underflow problems
    a = np.maximum(np.minimum(a, 50), -50)
    #f = 1./(1+exp(-a));
    f = np.exp(a) / (1+np.exp(a))
    return f


if __name__ == '__main__':
    
    # Classification
    print('Loading data ...')
    with open('../datasets/toy_10tasks_clf.pkl', 'rb') as fh:
        x, y, dimension, ntasks = pickle.load(fh)

    ntasks = len(x)  # get number of tasks
    dimension = x[0].shape[1]  # get problem dimension

    Omega = np.eye(ntasks)
    lambda_reg = 0.5
    w = -0.05 + 0.1*np.random.rand(dimension*ntasks, )
    eps = [np.sqrt(np.finfo(float).eps)]*ntasks*dimension
    r = spo.check_grad(logloss, logloss_der, w, x, y, Omega, lambda_reg)
    print(r)