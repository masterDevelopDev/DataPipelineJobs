import torch
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

class ImageEmbedder:
    def __init__(self, model):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = model.to(self.device)
 
    def embed_images(self, dataloader):
        self.model.eval()  # Set the model to evaluation mode
        features_list = []
        with torch.no_grad():  # Disable gradient calculation
            for batch in dataloader:
                # Move the batch of images to the device
                images = batch[0].to(self.device)
                # Encode the batch of images and collect the features
                features = self.model.encode_image(images)
                features_list.append(features.cpu())  # Move the features to CPU if you need to work with them on CPU later
        # Concatenate the list of feature batches into a single tensor
        return torch.cat(features_list, dim=0)

    def generate_image_embeddings(self, preprocessed_images_input, batch_size=32):
        dataset = TensorDataset(preprocessed_images_input)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
        features = self.embed_images(dataloader)
        return features
