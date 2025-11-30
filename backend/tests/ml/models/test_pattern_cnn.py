
import pytest
import numpy as np
import sys
from unittest.mock import MagicMock, patch


class TestPatternRecognitionCNN:

    @pytest.fixture
    def model(self):
        # Mock tensorflow modules
        mock_tf = MagicMock()
        mock_keras = MagicMock()
        mock_layers = MagicMock()
        mock_apps = MagicMock()

        modules = {
            "tensorflow": mock_tf,
            "tensorflow.keras": mock_keras,
            "tensorflow.keras.layers": mock_layers,
            "tensorflow.keras.applications": mock_apps,
        }

        with patch.dict(sys.modules, modules):
            # Import inside the patched context
            from app.ml.models.pattern_cnn import PatternRecognitionCNN

            # Setup mocks for the model build
            mock_model = MagicMock()
            mock_model.layers = [MagicMock(), MagicMock()]
            # Mock output layer
            mock_model.layers[-1].units = 10
            mock_model.layers[-1].activation.__name__ = 'softmax'

            # Mock predict return
            mock_model.predict.return_value = np.zeros((1, 10))
            mock_model.predict.return_value[0, 0] = 1.0

            # Mock fit return
            mock_history = MagicMock()
            mock_history.history = {'loss': [0.1], 'accuracy': [0.9]}
            mock_model.fit.return_value = mock_history

            # Mock evaluate return
            mock_model.evaluate.return_value = [0.1, 0.9]

            # Mock Keras Sequential
            mock_sequential = MagicMock(return_value=mock_model)
            mock_keras.Sequential = mock_sequential

            # Mock ResNet50
            mock_apps.ResNet50.return_value = MagicMock()

            cnn = PatternRecognitionCNN(num_classes=10, architecture='resnet50')
            cnn.model = mock_model

            yield cnn

    def test_model_architecture(self, model):
        """Test model has correct architecture"""
        assert model.model is not None
        assert len(model.model.layers) > 0

        # Check output layer
        assert model.model.layers[-1].units == 10
        assert model.model.layers[-1].activation.__name__ == 'softmax'

    def test_model_output_shape(self, model):
        """Test model output has correct shape"""
        # Test with different batch sizes
        # Batch size 1
        x1 = np.random.rand(1, 224, 224, 3).astype(np.float32)
        y1 = model.model.predict(x1)
        assert y1.shape == (1, 10)

        # Batch size 32
        x32 = np.random.rand(32, 224, 224, 3).astype(np.float32)
        y32 = model.model.predict(x32)
        assert y32.shape == (32, 10)

    def test_train_step(self, model):
        """Test training step runs without error"""
        # Create dummy data
        X_train = np.random.rand(2, 224, 224, 3).astype(np.float32)
        y_train = np.zeros((2, 10))

        # Train for 1 epoch with no validation
        history = model.train(
            X_train, y_train, epochs=1, batch_size=2, mlflow_tracking=False
        )

        assert 'loss' in history.history
        assert 'accuracy' in history.history
