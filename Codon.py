import re
#from pwn import remote
from random import choice

#  The predicted mapping of the codons
mapping =   {"AAA":'y',
             "AAC":'q',
             "AAG":'k',
             "AAT":'',
             "ACA":'q',
             "ACC":'1',
             "ACG":'s',
             "ACT":'0',
             "AGA":'~',
             "AGC":'',
             "AGG":'=',
             "AGT":'j',
             "ATA":' ',
             "ATC":'',
             "ATG":'i',
             "ATT":'',
             "CAA":'',
             "CAC":'',
             "CAG":'',
             "CAT":'',
             "CCA":'b',
             "CCC":'',
             "CCG":'w',
             "CCT":'v',
             "CGA":'a',
             "CGC":'h',
             "CGG":'',
             "CGT":'',
             "CTA":'x',
             "CTC":'',
             "CTG":'u',
             "CTT":'z',
             "GAA":'',
             "GAC":'',
             "GAG":'4',
             "GAT":'.',
             "GCA":'3',
             "GCC":'',
             "GCG":'/',
             "GCT":':',
             "GGA":'o',
             "GGC":'e',
             "GGG":'',
             "GGT":'f',
             "GTA":'',
             "GTC":'',
             "GTG":'p',
             "GTT":'c',
             "TAA":'',
             "TAC":'',
             "TAG":'2',
             "TAT":'',
             "TCA":'r',
             "TCC":'m',
             "TCG":',',
             "TCT":'n',
             "TGA":'',
             "TGC":'l',
             "TGG":'',
             "TGT":'',
             "TTA":'<',
             "TTC":'t',
             "TTG":'d',
             "TTT":'g'}


# The type of questions dina asks and the position of the string in them
question_types = {'send the string': 4,
                  'send the message': 5,
                  'send this back': 4,
                  'go ahead and send': 5,
                  'back to me': 2,
                  'enter this back': 7,
                  'please respond with': 4,
                  'respond with': 3,
                  'enter the string': 4,
                  'please send back': 4,
                  'send back': 3,
                  }


def beautify_data(msg):
      return str(msg)[2:-3].replace("\\n","")

# frequency analysis stuff
frequency = { a: 0 for a in mapping }
letter_frequency = list(' etaoinsrhldcumfgpywb,.vk-\"_\'x)(;0j1q=2:z/*!?$35>\{\}49[]867\\+|&<%@#^`~.,')
for i in range(len(letter_frequency)):
      if letter_frequency[i] in mapping.values():
            letter_frequency[i] = choice(letter_frequency)
letter_frequency = ''.join(letter_frequency)


for _ in range(100):
      s = 'CACCCGAACAACCACTCTCAGACGCTTTCTCTGGGCCGCCGACAGGAAAGACCACCGGAACTGCGAAGCGAACAGACATGTAACAGACGATCG'
      index = 0
      while 1:

            # Recieves until a message is sent
            ciphertext = ''
            try:
                  while ciphertext == '':
                        ciphertext = beautify_data(s)
            except EOFError:
                  s.close()
                  break
            # Checks if the flag is given
            if 'flag' in ciphertext:
                  print(ciphertext)
                  exit(0)

            # Find the frequency of each codon for frequency analysis
            for i in range(0,len(ciphertext),3):
                  frequency[ciphertext[i:i+3]] = frequency[ciphertext[i:i+3]] + 1
            frequency =  {k:frequency[k] for k in sorted(frequency, key= frequency.get, reverse=True)}

            # The mapping letters from frequency analysis
            frequency_letters = []
            # The whole plaintext
            plaintext = []
            for i in range(0,len(ciphertext),3):
                  # Checks if the mapping for the codon is known, if not predict a letter otherwise uses the mapping
                  if mapping[ciphertext[i:i+3]] == '':
                         plaintext.append(letter_frequency[list(frequency.keys()).index(ciphertext[i:i+3])])
                         frequency_letters.append((ciphertext[i:i+3],letter_frequency[list(frequency.keys()).index(ciphertext[i:i+3])]))
                  else:
                        plaintext.append(mapping[ciphertext[i:i+3]])

            plaintext = ''.join(plaintext)
            if 'nope' in plaintext:
                  break

            print(ciphertext)
            print(plaintext)
            print(str(index) + ": " + str(frequency_letters))

            response = 'random'
            for q in question_types.keys():
                  if q in plaintext:
                        response = plaintext.split(" ")[question_types[q]]
                        break

            print(response)
            s.send(response.upper())
            index += 1

print(frequency)