import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.autograd import Variable
from torch.utils import data
from torch.utils.data import DataLoader
from pyxtal_ml.ml.torch_dataset import dataset


class dl_torch():
    """
    A class for running PyTorch Neural Network.
    
    Args:
        feature: an array of descriptors.
        prop: the materials property to be predicted.
        tag: dictionary of feature and prop.
        hidden_layers: a dictionary for number of layers and number of neurons in
                       each layer.
        n_epoch: number of iterations.
        learning_rate: step for optimization.
        test_size: percentage of test datasets. (default = 0.3)
    
    """    
    def __init__(self, feature, prop, tag, hidden_layers, 
                 n_epoch = 300, batch_size = 64, learning_rate = 1e-3, test_size = 0.3):
        self.feature = np.asarray(feature)
        self.prop = np.asarray(prop)
        self.tag = tag
        self.n_epoch = n_epoch
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.test_size = test_size
        self.feature_size = len(self.feature[1])
        self.algo = 'PyTorch'
        
        # Split data into training and testing sets
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.feature, self.prop, test_size = self.test_size, random_state = 0)
        Dset = dataset(np.column_stack((self.X_train, self.Y_train)))
        train_loader = DataLoader(dataset=Dset,
                batch_size = self.batch_size,
                shuffle = True)

        # From numpy to torch tensor
        self.X_test = torch.tensor(self.X_test, requires_grad = True)
        self.X_test = self.X_test.type(torch.FloatTensor)
        
        # Read the hidden layers information
        self.n_layers, self.n_neurons = hidden_layers.values()
        
        # Building Neural Network architecture using Net class
        self.model = self.Linear_Torching(self.feature_size, self.n_layers, self.n_neurons)
        
        # Learning parameter for NN
        optimizer = optim.Adam(self.model.parameters(), lr = self.learning_rate, amsgrad=True)
        loss_func = nn.MSELoss()

        # Training step
        for epoch in range(self.n_epoch):
            for i, data in enumerate(train_loader, 0):
                X_train, Y_train = data
                X_train, Y_train = Variable(X_train).float(), Variable(Y_train).float()

                self.y_train = self.model(X_train)
                loss = loss_func(self.y_train, Y_train)
                
                #print('Number of epoch: ', t, i, loss.data[0])
            
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                print('Train epoch: {} [{}/{} ({:.0f}%)]\t\t\t Loss:{:.6f}'.format(
                    epoch, i*len(X_train), len(train_loader.dataset),
                    100.*i/len(train_loader), loss.data[0]))
        
        # Evaluation
        self.model.eval()
        with torch.no_grad():
            self.y_test = self.model(self.X_test)
            
        # From torch tensor back to numpy
        self.X_test = self.X_test.data.numpy()
        self.y_test = self.y_test.data.numpy()
            
        # Metrics
        self.r2 = r2_score(self.Y_test, self.y_test, sample_weight=None)
        self.mae = mean_absolute_error(self.y_test, self.Y_test)
    
    def convert2tensor(self, x):
        x = torch.FloatTensor(x)
        return x

    class Linear_Torching(nn.Module):
        """
        A class for the neural network (NN) architecture defined by users. This 
        NN is adopted from PyTorch. In this model, linear NN is implemented.
        
        Args:
            feature_size: number of features to be fed into the input neuron.
            n_layers: number of deep neural layers.
            n_neurons: number of neurons in each layers. This is in an array form.
        
        """
        def __init__(self, feature_size, n_layers, n_neurons):
            super().__init__()
            self.feature_size = feature_size
            self.n_layers = n_layers
            self.n_neurons = n_neurons
            
            if n_layers > 1:
                if len(n_neurons) > 1:              # different sizes of neurons in layers
                    self.h1 = nn.Linear(feature_size, n_neurons[0])
                    self.hidden = []
                    for i in range(n_layers-1):
                        self.hidden.append(nn.Linear(n_neurons[i], n_neurons[i+1]))
                    self.predict = nn.Linear(n_neurons[n_layers-1], 1)
                    
                else:                               # same size of neurons in layers
                    self.h1 = nn.Linear(feature_size, n_neurons[0])
                    self.hidden = []
                    for i in range(n_layers-1):
                        self.hidden.append(nn.Linear(n_neurons[0], n_neurons[0]))
                    self.predict = nn.Linear(n_neurons[0], 1)
                    
            else:
                self.h1 = nn.Linear(feature_size, n_neurons[0])
                self.predict = nn.Linear(n_neurons[0], 1)
                
        def forward(self, x):
            out = F.relu(self.h1(x))
            if self.n_layers > 1:
                for hid in self.hidden:
                    out = hid(out)
                    out = F.relu(out)
            else:
                pass
            out = self.h1(x).clamp(min=0)
            out = self.predict(out)
            return out
        
        def plot_correlation(self, figname=None, figsize=(12,8)):
            """
            Plot the correlation between prediction and target values.
            """
            plt.figure(figsize=figsize)
            plt.scatter(self.y_test, self.Y_test, c='green', label='test')
            plt.scatter(self.y_train, self.Y_train, c='blue', label='train')
            plt.title('{0:d} materials, r$^2$ = {1:.4f}, Algo: {2:s}'.format(len(self.prop), self.r2, self.algo))
            plt.xlabel('Prediction')
            plt.ylabel(self.tag['prop'])
            plt.legend()
            if figname is None:
                plt.show()
            else:
                plt.savefig(figname)
                plt.close()
            
    def plot_distribution(self, figname=None, figsize=(12,8)):
        """
        some other plots to facilate the results
        """
        plt.figure(figsize=figsize)
        plt.hist(self.Y, bins = 100)
        plt.xlabel(self.tag['prop'])
        if figname is None:
            plt.show()
        else:
            plt.savefig(figname)
            plt.close()
       

    def print_summary(self):
        """
        print the paramters and performances
        """
        print("----------------------------------------")
        print("-------------SUMMARY of ML--------------")
        print("----------------------------------------")
        print("Number of samples:  {:20d}".format(len(self.prop)))
        print("Number of features: {:20d}".format(len(self.feature[0])))
        print("Algorithm:          {:>20}".format(self.algo))
        print("Feature:            {:>20}".format(self.tag['feature']))
        print("Property:           {:>20}".format(self.tag['prop']))
        print("r^2:              {:22.4f}".format(self.r2))
        print("MAE:              {:22.4f}".format(self.mae))
