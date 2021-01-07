import tensorflow as tf
from numpy import hstack
from numpy import zeros
from numpy import ones
from numpy.random import rand
from numpy.random import randn
from keras.models import Sequential
from keras.layers import Dense
from matplotlib import pyplot as plt
import pandas as pd
from keras.layers.advanced_activations import LeakyReLU
from matplotlib.lines import Line2D


def generator_model():
    model = tf.keras.Sequential()
    model.add(layers.Dense(7*7*256, use_bias=False, input_shape=(1735,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Reshape((7, 7, 256)))
    assert model.output_shape == (None, 7, 7, 256) # Note: None is the batch size
    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    assert model.output_shape == (None, 7, 7, 128)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    assert model.output_shape == (None, 14, 14, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    assert model.output_shape == (None, 28, 28, 1)

    return model
	
	
	
def discriminator_model():
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', input_shape=[28, 28, 1]))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(1))

    return model
	
	
	
relu_alpha = 0.3
def define_discriminator(n_inputs=2):
    model = Sequential()
    model.add(Dense(1000,  kernel_initializer='he_uniform', input_dim=n_inputs))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(500,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(250,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(100,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(50,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model
	
	
	
def define_generator(latent_dim, n_outputs=2):
    model = Sequential()
    model.add(Dense(1000, activation='relu', kernel_initializer='he_uniform', input_dim=latent_dim))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(500,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(250,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(100,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(50,  kernel_initializer='he_uniform'))
    model.add(LeakyReLU(alpha=relu_alpha))
    model.add(Dense(n_outputs, activation='linear'))
    return model


def define_gan(generator, discriminator):
    discriminator.trainable = False
    model = Sequential()
    model.add(generator)
    model.add(discriminator)
    model.compile(loss='binary_crossentropy', optimizer='adam')
    return model

def generate_real_samples(n):
    df = pd.read_csv('resampled.csv', header=None) 
    X1 = df[0].to_numpy()[0:n]
    X2 = df[1].to_numpy()[0:n]
    X1 = X1.reshape(n, 1)
    X2 = X2.reshape(n, 1)
    X = hstack((X1, X2))

    y = ones((n, 1))
    return X, y

def generate_latent_points(latent_dim, n):
    x_input = randn(latent_dim * n)
    x_input = x_input.reshape(n, latent_dim)
    return x_input

def generate_fake_samples(generator, latent_dim, n):
    x_input = generate_latent_points(latent_dim, n)
    X = generator.predict(x_input)
    y = zeros((n, 1))
    return X, y


def summarize_performance(epoch, generator, discriminator, latent_dim, n=1735):
    x_real, y_real = generate_real_samples(n)
    _, acc_real = discriminator.evaluate(x_real, y_real, verbose=0)
    x_fake, y_fake = generate_fake_samples(generator, latent_dim, n)
    _, acc_fake = discriminator.evaluate(x_fake, y_fake, verbose=0)
    print(epoch+1, acc_real, acc_fake)


    custom_lines = [Line2D([0], [0], color='red', lw=4), Line2D([0], [0], color='blue', lw=4)]
    plt.rcParams.update({'font.size': 24})
    fig, ax = plt.subplots(figsize=(30,9))
    ax.legend(custom_lines, ['real data', 'generated data'])
    ax.set(xlabel='time (100ms)', ylabel='motor load')


    plt.scatter(x_fake[:, 0], x_fake[:, 1], color='blue')
    plt.plot(x_real[:, 0], x_real[:, 1], color='red', linewidth=4)

    plt.savefig('vis/gan_epoch_' + str(epoch+1))


def train(g_model, d_model, gan_model, latent_dim, n_epochs=1000000, n_batch=1735, n_eval=2000):
    half_batch = int(n_batch / 2)
    for i in range(n_epochs):
        x_real, y_real = generate_real_samples(half_batch)
        x_fake, y_fake = generate_fake_samples(g_model, latent_dim, half_batch)
        d_model.train_on_batch(x_real, y_real)
        d_model.train_on_batch(x_fake, y_fake)
        x_gan = generate_latent_points(latent_dim, n_batch)
        y_gan = ones((n_batch, 1))
        gan_model.train_on_batch(x_gan, y_gan)
        if (i+1) % n_eval == 0:
            summarize_performance(i, g_model, d_model, latent_dim)



physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)

latent_dim = 5
discriminator = define_discriminator()
generator = define_generator(latent_dim)
gan_model = define_gan(generator, discriminator)
train(generator, discriminator, gan_model, latent_dim)
	
	
