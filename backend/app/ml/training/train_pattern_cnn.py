
import argparse
import os

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from app.ml.models.pattern_cnn import PatternRecognitionCNN


def train_model(data_dir, epochs=50, batch_size=32):
    """Train the pattern recognition model"""

    # Data generators with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        # Patterns like H&S are not symmetric horizontally in meaning
        horizontal_flip=False,
        zoom_range=0.1,
        validation_split=0.2
    )

    # Load data
    train_data = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    val_data = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    # Build and train model
    model = PatternRecognitionCNN(
        num_classes=train_data.num_classes, architecture="resnet50"
    )
    model.build_model()

    print(model.model.summary())

    # Train
    history = model.train(
        train_data=train_data,
        val_data=val_data,
        epochs=epochs,
        batch_size=batch_size,
        mlflow_tracking=True
    )
    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Pattern Recognition CNN")
    parser.add_argument(
        "--data_dir", type=str, required=True, help="Path to dataset directory"
    )
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")

    args = parser.parse_args()
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory {args.data_dir} not found.")
        exit(1)

    train_model(args.data_dir, args.epochs, args.batch_size)
