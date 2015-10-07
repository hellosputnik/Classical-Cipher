#!/usr/bin/env python

import math
import operator
import sys

# This string holds all the characters in the English alphabet
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# This dictionary holds the regular frequencies for all the characters in the English alphabet
regular_frequency = { 
  'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702, 'F': 0.02228, 
  'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153, 'K': 0.00772, 'L': 0.04025,
  'M': 0.02406, 'N': 0.06749, 'O': 0.07507, 'P': 0.01929, 'Q': 0.00095, 'R': 0.05987,
  'S': 0.06327, 'T': 0.09056, 'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150,
  'Y': 0.01974, 'Z': 0.00074
}

# This dictionary holds the different types of ciphers
ciphers = { "Rail Fence": 0, "Caesar": 1, "Vigenere": 2 }

def load_ciphertext(filename):
  """ This method returns the entire file content as a string. """
  with open(filename, 'r') as file:
    data = file.read()
    
  # Return the entire file as a string
  return data

def frequency_analysis(text, fraction = False):
  """ This method will perform a frequency analysis on a string. """

  # Create an empty dictionary to hold and count the occurrences of each character
  frequencies = {}
  
  # For each character in the string, add or increment the character in the dictionary
  for  character in text:
    if character in frequencies:
      frequencies[character] += 1.0
    else:
      frequencies[character] =  1.0
  
  # If the fraction flag is true, divide each entry in the dictionary by the length
  if fraction:
    for character in frequencies:
       frequencies[character] /= len(text)

  # Return the constructed frequency dictionary
  return frequencies
  
def correlation_of_frequency(frequencies):
  """ This method will calculate the correlation of frequency on a dictionary of frequencies. """
  
  # phi = summation of f(c) p((c - i) % 26) from i = 0 to 25 for each c
  
  # f(c) is the frequency of character c
  # p(x) is the frequency of character x on average (i.e. regular frequency)

  # The number 26 in the modulo operation is derived from the number of characters in the English alphabet
  # a = 0, b = 1, c = 2, ..., z = 25

  # Create an empty dictionary to hold the correlation of frequencies
  correlation = {}
  
  # For i = 0 to i = 25 and for each character 'c', calculate phi
  for i in range(26):
    phi = 0
    for frequency in frequencies:
      phi += frequencies[frequency] * regular_frequency[alphabet[(alphabet.index(frequency) - i) % 26]]
    correlation[i] = phi
  
  # Return the dictionary of phi values
  return correlation

def index_of_coincidence(text, size):
  """ This method will return a calculated estimation of the key length based on correlation of frequencies. """
  
  # Create a variable for the coincidence counting
  coincidence = 0
  
  # For each i-th column, calculate the index of coincidence
  for column in range(size):
  
    # Construct a string of all the letters in a single column
    offset, index, string = 0, 0, ""
    while column + offset < len(text): # equivalent to column + (offset * size); offset += 1;
      string  += text[column + offset]
      offset  += size
      
    # Run a frequency analysis on the constructed string
    frequencies = frequency_analysis(string)
    
    # Calculate the column index of coincidence
    for frequency in frequencies:
        index += (frequencies[frequency] * (frequencies[frequency] - 1))
    index /= (len(string) * (len(string) - 1 ) / 26.0)
    
    # Add the column index of coincidence
    coincidence += index
  
  # Divide by the number of columns to calculate the average index of coincidence
  coincidence /= size
  
  # Return the average calculated index of coincidence
  return coincidence
  
def bigram_analysis(text):
  """ This method will perform a custom bigram analysis on a string. """

  # Create an empty dictionary to hold and count the occurrences of each bigram
  frequencies = {}
  
  # Create counter variables to help create substrings
  # In an n-gram analysis (where user inputs 'n'), right is set to n. In this case, n = 2.
  left, right = 0, 2
  while right != len(text):
    if text[left:right] in frequencies:
      frequencies[text[left:right]] += 1
    else:
      frequencies[text[left:right]]  = 1
    left  += 1
    right += 1
 
  # Statistically, the frequency of TH > HE > ER > AN. Source: http://www.cryptograms.org/letter-frequencies.php
  if frequencies['TH'] >= frequencies['HE'] and frequencies['HE'] >= frequencies['ER'] and frequencies['ER'] >= frequencies['AN']:
    return True
  
  return False
    
def get_key(text, length = 1):
  """ This method will estimate the key given the text and key length. """
  
  # Create a variable to hold the key
  key = ""
  
  # For each column (i.e. key length), estimate the character used to encrypt
  for column in range(length):
    offset, string = 0, ""
    while column + offset < len(text):
      string += text[column + offset]
      offset += length
    # Return the character with the highest phi value returned from the correlation of frequency
    key += alphabet[max(correlation_of_frequency(frequency_analysis(string, True)).iteritems(), key = operator.itemgetter(1))[0]]
    
  # Return the estimated key
  return key
  
def decrypt(text, cipher, key = 'A'):
  """ This method decrypts the text from ciphertext to plaintext. """
  
  # Create a variable to hold the plaintext
  plaintext = ""
  
  # Rail Fence cipher
  if ciphers[cipher] == 0:
    size = 2
    while True:
      plaintext = ""
      rows = int(math.ceil(len(text) / size))
      for column in range(rows):
        offset = 0
        while column + offset < len(text):
          plaintext += text[column + offset]
          offset += rows
      if bigram_analysis(plaintext):
        break
      size += 1
  
  # Caesar cipher
  if ciphers[cipher] == 1:
    for character in text:
      plaintext += alphabet[(alphabet.index(character) - alphabet.index(key)) % 26]
  
  # Vigenere cipher
  if ciphers[cipher] == 2:
    offset = 0
    for character in text:
      plaintext += alphabet[(alphabet.index(character) - alphabet.index(key[offset % len(key)])) % 26]
      offset += 1
      
  return plaintext

def main():
  # Handle CLI arguments
  if len(sys.argv) < 2:
    filename = raw_input("\nFilename: ")
  else:
    filename = sys.argv[1]
    print "\nFilename: %s" % filename
  
  # Load the ciphertext
  print "\nLoading file....................",
  ciphertext = load_ciphertext(filename)
  print "DONE\n"

  # Calculate the index of coincidence
  MAX = len(ciphertext) / 2
  print "Calculating the key length......",
  length  = 1
  counter = 1
  while index_of_coincidence(ciphertext, length) < 1.4:
    length  += 1
    counter += 1
    if counter == MAX:
      length = 0
      break
      
  # print index_of coincidence(ciphertext, length) to see IC value
      
  # The ciphertext's key is quite large. This is probably a one-time pad cipher.
  if length == 0:
    print "ERROR\n"
    print "Based on calculated index of coincidence values, this text is probably encrypted with a one-time pad encryption.\n"
    return
  print "DONE\n"
  
  # Estimate the key
  print "Estimating the key..............",
  key = get_key(ciphertext, length)
  print "DONE\n"
  
  print "Estimated key: '%s'\n" % key
  
  # Keys with a length of 1 are either Caesar or Rail Fence. Otherwise, the encryption is Vigenere as One-Time pad has already been ruled out.
  if length == 1:
    if key == 'A':
      print "Based on the key (i.e. key = 'A'), the text is probably encrypted with a Rail Fence cipher.\n"
      plaintext = decrypt(ciphertext, "Rail Fence", key)
    else:     
      print "Based on the key and its length (i.e. key length = 0 but key != 'A'), the text is probably encrypted with a Caesar cipher.\n"
      plaintext = decrypt(ciphertext, "Caesar", key)
  elif length > 1:
      print "Based on the key and its length (i.e. key length > 1), the text is probably encrypted with a Vigenere cipher.\n"
      plaintext = decrypt(ciphertext, "Vigenere", key)
  else:
    plaintext = "NOOOOOO! You're not suppose to see this! Look away!\n"
    
  print "The first 150 characters of the plaintext is...\n\n%s\n" % plaintext[:151]

if __name__ == '__main__':
  main();
  
# Last updated: September 9, 2014VgjbhyqagorQrspbajvgubhgbhetbbqsevraqPnrfne
