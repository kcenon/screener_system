from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB0, ResNet50


class PatternRecognitionCNN:
    """CNN model for chart pattern recognition"""

    def __init__(self, num_classes=10, architecture="resnet50"):
        self.num_classes = num_classes
        self.architecture = architecture
        self.model = None

    def build_model(self):
        """Build CNN model with transfer learning"""

        # Load pre-trained base model
        if self.architecture == "resnet50":
            base_model = ResNet50(
                include_top=False, weights="imagenet", input_shape=(224, 224, 3)
            )
        elif self.architecture == "efficientnet":
            base_model = EfficientNetB0(
                include_top=False, weights="imagenet", input_shape=(224, 224, 3)
            )
        else:
            raise ValueError(f"Unsupported architecture: {self.architecture}")

        # Freeze base model layers
        base_model.trainable = False

        # Add custom classification head
        model = keras.Sequential(
            [
                base_model,
                layers.GlobalAveragePooling2D(),
                layers.Dense(512, activation="relu"),
                layers.Dropout(0.5),
                layers.BatchNormalization(),
                layers.Dense(256, activation="relu"),
                layers.Dropout(0.5),
                layers.Dense(self.num_classes, activation="softmax"),
            ]
        )

        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        self.model = model
        return model

    def train(
        self, train_data, val_data, epochs=50, batch_size=32, mlflow_tracking=True
    ):
        """Train the model"""

        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6
            ),
        ]

        # MLflow tracking
        if mlflow_tracking:
            import mlflow
            import mlflow.keras

            with mlflow.start_run(run_name=f"pattern_cnn_{self.architecture}"):
                mlflow.log_params(
                    {
                        "architecture": self.architecture,
                        "num_classes": self.num_classes,
                        "epochs": epochs,
                        "batch_size": batch_size,
                        "optimizer": "Adam",
                        "learning_rate": 0.001,
                    }
                )

                # Train
                history = self.model.fit(
                    train_data,
                    validation_data=val_data,
                    epochs=epochs,
                    batch_size=batch_size,
                    callbacks=callbacks,
                )

                # Log metrics
                mlflow.log_metrics(
                    {
                        "train_accuracy": history.history["accuracy"][-1],
                        "val_accuracy": history.history["val_accuracy"][-1],
                        "train_loss": history.history["loss"][-1],
                        "val_loss": history.history["val_loss"][-1],
                    }
                )

                # Log model
                mlflow.keras.log_model(self.model, "model")

        else:
            history = self.model.fit(
                train_data,
                validation_data=val_data,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
            )

        return history

    def evaluate(self, test_data):
        """Evaluate model on test set"""
        results = self.model.evaluate(test_data)

        return {"test_loss": results[0], "test_accuracy": results[1]}
