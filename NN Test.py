import math
import random


# CLASS NET #
class Net:
    m_layers = list()
    m_error = 1.0
    m_recentAverageError = 1.0
    m_recentAverageSmoothingFactor = 100.0

    def __init__(self, _topology):
        numLayers = len(_topology)
        for layerNum in range(numLayers):
            self.m_layers.append(Layer())  # Find where m_layers is defined
            numOutputs = 0 if layerNum == numLayers - 1 else topology[layerNum + 1]

            # We have a new layer, now fill it with neurons, and
            # add a bias neuron in each layer.
            for neuronNum in range(topology[layerNum] + 1):
                self.m_layers[-1].append(Neuron(numOutputs, neuronNum))
                print("Made a Neuron!")

            # Force the bias node's output to 1.0 (it was the last neuron pushed in this layer):
            self.m_layers[-1][-1].setOutputVal(1.0)

    def feedForward(self, inputVals):
        assert len(inputVals) == len(self.m_layers[0]) - 1

        # Assign (latch) the input values into the input neurons
        for i in range(len(inputVals)):
            self.m_layers[0][i].setOutputVal(float(inputVals[i]))

        # forward propagate
        for layerNum in range(1, len(self.m_layers)):
            prevLayer = self.m_layers[layerNum - 1]
            for n in range(len(self.m_layers[layerNum]) - 1):
                self.m_layers[layerNum][n].feedForward(prevLayer)

    def backProp(self, targetVals):
        # Calculate overall net error (RMS of output neuron errors)

        outputLayer = self.m_layers[-1]
        m_error = 0.0

        for n in range(len(outputLayer) - 1):
            delta = targetVals[n] - outputLayer[n].getOutputVal()
            m_error += delta ** 2

        m_error /= len(outputLayer) - 1  # get average error squared
        m_error = math.sqrt(m_error)  # RMS

        # Implement a recent average measurement

        self.m_recentAverageError = (self.m_recentAverageError * self.m_recentAverageSmoothingFactor + m_error) / (
                self.m_recentAverageSmoothingFactor + 1.0)

        # Calculate output layer gradients

        for n in range(len(outputLayer) - 1):
            outputLayer[n].calcOutputGradients(targetVals[n])

        # Calculate hidden layer gradients

        for layerNum in range(len(self.m_layers) - 2, 0, -1):
            hiddenLayer = self.m_layers[layerNum]
            nextLayer = self.m_layers[layerNum + 1]

            for n in range(len(hiddenLayer)):
                hiddenLayer[n].calcHiddenGradients(nextLayer)

        # For all layers from outputs to first hidden layer,
        # update connection weights

        for layerNum in range(len(self.m_layers) - 1, 0, -1):
            layer = self.m_layers[layerNum]
            prevLayer = self.m_layers[layerNum - 1]

            for n in range(len(layer) - 1):
                layer[n].updateInputWeights(prevLayer)

    def getResults(self, resultVals):
        resultVals.clear()

        for n in range(len(self.m_layers[-1]) - 1):
            resultVals.append(self.m_layers[-1][n].getOutputVal())

    def getRecentAverageError(self):
        return self.m_recentAverageError


# CLASS NEURON #
class Neuron:
    eta = 0.15
    alpha = 0.5
    m_outputVal = 0.0
    m_outputWeights = list()
    m_myIndex = 0.0
    m_gradient = 0.0

    def __init__(self, numOutputs, myIndex):
        for c in range(numOutputs):
            self.m_outputWeights.append(Connection())
            self.m_outputWeights[-1].weight = self.randomWeight()

        self.m_myIndex = myIndex

    def feedForward(self, prevLayer):
        _sum = 0.0

        # Sum the previous layer's outputs (which are our inputs)
        # Include the bias node from the previous layer.

        for n in range(len(prevLayer)):
            _sum += prevLayer[n].getOutputVal() * prevLayer[n].m_outputWeights[self.m_myIndex].weight

        self.m_outputVal = self.transferFunction(_sum)

    def transferFunctionDerivative(self, x):
        # tanh derivative

        return 1.0 - x ** 2

    def transferFunction(self, x):
        # tanh - output range [-1.0..1.0]

        return math.tanh(x)

    def calcOutputGradients(self, targetVal):
        delta = targetVal - self.m_outputVal
        self.m_gradient = delta * self.transferFunctionDerivative(self.m_outputVal)

    def calcHiddenGradients(self, nextLayer):
        dow = self.sumDOW(nextLayer)
        self.m_gradient = dow * self.transferFunctionDerivative(self.m_outputVal)

    def sumDOW(self, nextLayer):
        _sum = 0.0

        # Sum our contributions of the errors at the nodes we feed.

        for n in range(len(nextLayer) - 1):
            _sum += self.m_outputWeights[n].weight * nextLayer[n].m_gradient

        return _sum

    def updateInputWeights(self, prevLayer):
        # The weights to be updated are in the Connection container
        # in the neurons in the preceding layer

        for n in range(len(prevLayer)):
            neuron = prevLayer[n]
            oldDeltaWeight = neuron.m_outputWeights[self.m_myIndex].deltaWeight

            newDeltaWeight = (
                # Individual input, magnified by the gradient and train rate:
                    self.eta
                    * neuron.getOutputVal()
                    * self.m_gradient
                    # Also add momentum = a fraction of the previous delta weight;
                    + self.alpha
                    * oldDeltaWeight)

            neuron.m_outputWeights[self.m_myIndex].deltaWeight = newDeltaWeight
            neuron.m_outputWeights[self.m_myIndex].weight += newDeltaWeight

    def setOutputVal(self, val):
        self.m_outputVal = val

    def getOutputVal(self):
        return self.m_outputVal

    def randomWeight(self):
        return random.uniform(0, 1)


# CLASS TRAINGINGDATA #
class TrainingData:
    m_trainingDataFile = None  # type: BufferedReader I think

    def __init__(self, filename):
        self.m_trainingDataFile = open(filename)

    # Returns the number of input values read from the file:
    def getTargetOutputs(self, targetOutputVals):
        targetOutputVals.clear()

        line = self.m_trainingDataFile.readline().split()
        label = line[0]

        if label == "out:":
            for oneValue in line[1:]:
                targetOutputVals.append(float(oneValue))

        return len(targetOutputVals)

    def getNextInputs(self, inputVals):
        inputVals.clear()

        line = self.m_trainingDataFile.readline().split()
        if len(line) == 0:
            return -1

        label = line[0]

        if label == "in:":
            for oneValue in line[1:]:
                inputVals.append(float(oneValue))

        return len(inputVals)

    def getTopology(self, _topology):
        line = self.m_trainingDataFile.readline().split()
        label = line[0]

        if label == "topology:":
            for n in line[1:]:
                _topology.append(int(n))


class Connection:
    weight = 0
    deltaWeight = 0


Layer = list


def showVectorVals(label, v):
    print(label, end=" ")
    for i in range(len(v)):
        print(v[i], end=" ")
    print()


normalise_scale = 4
normalise_min = 1


def normalise_values(input_values):
    for i, n in enumerate(input_values):
        n /= normalise_scale
        n -= normalise_min - 1
        input_values[i] = n
    return input_values


def denormalise_values(output_values):
    for i, n in enumerate(output_values):
        n += normalise_min + 1
        n *= normalise_scale
        output_values[i] = n
    return output_values


# PROGRAM START #

trainData = TrainingData("training_data_xor.txt")

# e.g., { 3, 2, 1 }
topology = list()
trainData.getTopology(topology)

myNet = Net(topology)

inputVals, targetVals, resultVals = list(), list(), list()

trainingPass = 0

while True:
    trainingPass += 1

    # Get new input data and feed it forward:
    if trainData.getNextInputs(inputVals) != topology[0]:
        break

    print("Pass", trainingPass)

    showVectorVals("Inputs:", inputVals)
    normalise_values(inputVals)
    myNet.feedForward(inputVals)

    # Collect the net's actual output results:
    myNet.getResults(resultVals)

    denormedVals = list(resultVals)
    denormalise_values(denormedVals)
    showVectorVals("Outputs:", denormedVals)

    # Train the net what the outputs should have been:
    trainData.getTargetOutputs(targetVals)
    showVectorVals("Targets:", targetVals)
    assert len(targetVals) == topology[-1]

    myNet.backProp(targetVals)

    # Report how well the training is working, average over recent samples:
    print("Net recent average error:", myNet.getRecentAverageError())

print("Done")
