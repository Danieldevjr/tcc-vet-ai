import torch
import torch.nn as nn
from torchvision import models, transforms
import os

class EnsembleVeterinario(nn.Module):
    def __init__(self, num_classes):
        super(EnsembleVeterinario, self).__init__()
        self.resnet = models.resnet50(weights=None)
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, num_classes)
        self.effnet = models.efficientnet_b0(weights=None)
        self.effnet.classifier[1] = nn.Linear(self.effnet.classifier[1].in_features, num_classes)
        self.densenet = models.densenet121(weights=None)
        self.densenet.classifier = nn.Linear(self.densenet.classifier.in_features, num_classes)

    def forward(self, x):
        return (self.resnet(x) + self.effnet(x) + self.densenet(x)) / 3.0

def carregar_modelo_ia():
    nomes_das_classes = ['Demodicose', 'Dermatite', 'Hipersensibilidade', 'INCONCLUSIVO', 'Infecção Fúngica', 'Micose (Ringworm)', 'Pele Saudável']
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    modelo = EnsembleVeterinario(num_classes=len(nomes_das_classes))
    caminho_modelo = 'modelo_vet_ensemble_V2_7Classes.pth' 
    
    if os.path.exists(caminho_modelo):
        modelo.load_state_dict(torch.load(caminho_modelo, map_location=device, weights_only=True))
        modelo = modelo.to(device)
        modelo.eval()
        return modelo, device, nomes_das_classes
    return None, None, None

def get_transformacao():
    return transforms.Compose([
        transforms.Resize((224, 224)), 
        transforms.ToTensor(), 
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])