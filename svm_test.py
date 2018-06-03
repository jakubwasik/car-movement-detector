#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC


#generujemy dane dla problemu liniowo separowalnego
class1=np.random.multivariate_normal([1,3],[[1,0.7],[0.7,0.9]],20)
class2=np.random.multivariate_normal([6,2],[[0.6,0],[0,0.8]],20)
TrainData=np.vstack([class1[0:10,:],class2[0:10,:]])
print TrainData
TestData=np.vstack([class1[10:20,:],class2[10:20,:]])
TrainClasses=[0]*10+[1]*10
TestClasses=TrainClasses

#wykres ilustrujacy zbior uczacy w przestrzeni cech
plt.scatter(TrainData[0:10,0],TrainData[0:10,1],c='b')
plt.scatter(TrainData[10:20,0],TrainData[10:20,1],c='r')
plt.show()

#Parametry liniowego klasyfikatora SVM
svm = SVC(kernel="linear", C=100)

#Uczenie klasyfikatora
svm.fit(TrainData,TrainClasses)

#Obiekt nauczonego klasyfikatora przechowuje takie informacje jak:
print 'Numery probek bedace wektorami podpierajacymi'
print svm.support_
print 'Wektory zbioru uczacego bedace wektorami podpierajacymi'
print svm.support_vectors_
print 'Liczba wektrow podpierajacych w poszczegolnych klasach'
print svm.n_support_


#Optymalna hiperplaszczyzna rozdzialająca
w = svm.coef_[0]
a = -w[0] / w[1]
xx = np.linspace(-1, 7)
yy = a * xx - (svm.intercept_[0]) / w[1]

#Wyznaczamy proste równoległe do OSH odległe od niej o wartość marginesu
#Na prostych tych znajdują się wektory podpierające
b = svm.support_vectors_[0]
yy_down = a * xx + (b[1] - a * b[0])
b = svm.support_vectors_[-1]
yy_up = a * xx + (b[1] - a * b[0])

#Narysowanie OSH i prostych równoległych
plt.plot(xx, yy, 'k-')
plt.plot(xx, yy_down, 'k--')
plt.plot(xx, yy_up, 'k--')
#Zaznaczenie na wykresie wektorów podpierających
plt.scatter(svm.support_vectors_[:, 0], svm.support_vectors_[:, 1],
            s=80, facecolors='none')
plt.scatter(TrainData[:, 0], TrainData[:, 1], c=TrainClasses, cmap=plt.cm.Paired)

plt.axis('tight')
plt.show()

#Testowanie klasyfikatora na zbiorze uczącym
y = svm.predict(TestData)
print 'Etykiety klas dla zbioru testowego'
print y

#Sprawność klasyfikatora na zbiorze testowym
print 'Sprawność klasyfikatora:'
print svm.score(TestData,TestClasses)