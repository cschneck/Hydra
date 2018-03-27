# -*- coding: utf-8 -*-
###########################################################################
# Pre-processing raw text

# Date: November 2017
###########################################################################
import os
import re
import nltk # Natural Language toolkit
from nltk.tokenize import sent_tokenize, word_tokenize # form tokens from words/sentences
import matplotlib
matplotlib.use('Agg')
import string
import csv
from datetime import datetime
from collections import namedtuple, Counter
import itertools
from itertools import imap, permutations # set up namedtuple
from collections import defaultdict # create dictionary with empty list for values
import matplotlib.pyplot as plt # graphs
import networkx as nx
import numpy as np
########################################################################
## READING AND TOKENIZATION OF RAW TEXT (PRE-PROCESSING)

#TODO: move to a seperate file (up to readFile)
basic_pronouns = "I Me You She He Him It We Us They Them Myself Yourself Himself Herself Itself Themselves My your Her Its Our Their His"
possessive_pronouns = "mine yours his hers ours theirs my"
reflexive_pronouns = "myself yourself himself herself itself oneself ourselves yourselves themselves you've"
relative_pronouns = "that whic who whose whom where when"

male_honorific_titles = ['Mr', 'Sir', 'Lord', 'Master', 'Gentleman', 
						 'Sire', "Esq", "Father", "Brother", "Rev", "Reverend",
						 "Fr", "Pr", "Paster", "Br", "His", "Rabbi", "Imam",
						 "Sri", "Thiru", "Raj", "Son", "Monsieur", "M", "Baron",
						 "Prince", "King", "Emperor", "Grand Prince", "Grand Duke",
						 "Duke", "Sovereign Prince", "Count", "Viscount", "Crown Prince",
						 'Gentlemen', 'Uncle', 'Widower', 'Don']

female_honorific_titles = ['Mrs', 'Ms', 'Miss', 'Lady', 'Mistress',
						   'Madam', "Ma'am", "Dame", "Mother", "Sister",
						   "Sr", "Her", "Kum", "Smt", "Ayah", "Daughter",
						   "Madame", "Mme", 'Madame', "Mademoiselle", "Mlle", "Baroness",
						   "Maid", "Empress", "Queen", "Archduchess", "Grand Princess",
						   "Princess", "Duchess", "Sovereign Princess", "Countess",
							"Gentlewoman", 'Aunt', 'Widow']

ignore_neutral_titles = ['Dr', 'Doctor', 'Captain', 'Capt',
						 'Professor', 'Prof', 'Hon', 'Honor', "Excellency",
						 "Honourable", "Honorable",  "Chancellor", "Vice-Chancellor", 
						 "President", "Vice-President", "Senator", "Prime", "Minster",
						 "Principal", "Warden", "Dean", "Regent", "Rector",
						 "Director", "Mayor", "Judge", "Cousin", 'Archbishop',
						 'General', 'Secretary', 'St', 'Saint', 'San', 'Assistant']

connecting_words = ["of", "the", "De", "de", "La", "la", 'al', 'y', 'Le']

words_to_ignore = ["Mr", "Mrs", "Ms", "Dr", "sir", "Sir", "SIR", "Dear", "DEAR", 
				   "CHAPTER", "VOLUME", "MAN", "God", "god", "O", "anon",
				   "Ought", "ought", "thou", "thither", "yo", "Till", "ay",
				   "Hitherto", "Ahoy", "Alas", "Yo", "Chapter", "Again", "'d",
				   "If", "thy", "Thy", "thee", "suppose", "there", "'There", "no-one", "No-one",
				   "good-night", "Good-night", "good-morning", "Good-moring", 'to-day', 'to-morrow',
				   'To-day', 'To-morrow', 'to-night', 'To-night', 'thine', 'Or', "d'you"]

words_to_ignore += ["".join(a) for a in permutations(['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X'], 2)]
words_to_ignore += ["".join(a) for a in ['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X', 'XV']]

words_to_ignore += ["Chapter {0}".format("".join(a)) for a in permutations(['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X'], 2)]
words_to_ignore += ["Chapter {0}".format("".join(a)) for a in ['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X']]

words_to_ignore += ["Chapter {0}".format("".join(a)) for a in permutations(['1','2','3','4','5','6','7','8','9','10'], 2)]
words_to_ignore += ["Chapter {0}".format("".join(a)) for a in ['1','2','3','4','5','6','7','8','9','10']]

words_to_ignore += ["CHAPTER {0}".format("".join(a)) for a in permutations(['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X'], 2)]
words_to_ignore += ["CHAPTER {0}".format("".join(a)) for a in ['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X']]

words_to_ignore += ["Volume {0}".format("".join(a)) for a in permutations(['1','2','3','4','5','6','7','8','9','10'], 2)]
words_to_ignore += ["Volume {0}".format("".join(a)) for a in ['1','2','3','4','5','6','7','8','9','10']]

words_to_ignore += ["Volume {0}".format("".join(a)) for a in permutations(['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X'], 2)]
words_to_ignore += ["Volume {0}".format("".join(a)) for a in ['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X']]

words_to_ignore += ["VOLUME {0}".format("".join(a)) for a in permutations(['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X'], 2)]
words_to_ignore += ["VOLUME {0}".format("".join(a)) for a in ['I', 'II','III', 'IV', 'VI', 'XX', 'V', 'X']]

words_to_ignore += ["VOLUME {0}".format("".join(a)) for a in permutations(['1','2','3','4','5','6','7','8','9','10'], 2)]
words_to_ignore += ["VOLUME {0}".format("".join(a)) for a in ['1','2','3','4','5','6','7','8','9','10']]


def readFile(filename):
	file_remove_extra = []
	with open(filename, "r") as given_file:
		string_words = given_file.read()
		string_words = string_words.replace("\n", " ")
		string_words = string_words.replace(";" , " ")
		string_words = string_words.replace("--", ", ")
		string_words = string_words.replace("_", "")
		string_words = string_words.replace("'I", "' I") # fix puncutation where I 
		string_words = string_words.replace("'It", "' It")
		string_words = string_words.replace("'we", "' we")
		string_words = string_words.replace("'We", "' We")
		string_words = string_words.replace("Mr.", "Mr") # period created breaks when spliting
		string_words = string_words.replace("Ms.", "Ms")
		string_words = string_words.replace("Mrs.", "Mrs")
		string_words = string_words.replace("Dr.", "Dr")
		string_words = string_words.replace("St.", "St")
		# replace utf-8 elements
		string_words = string_words.replace("’", "\'") # replace signal quotes
		string_words = string_words.replace("“", "~\"") # isolate dialouge double quotes
		string_words = string_words.replace("” ", "\"~")

		string_words = re.sub(r'[\x90-\xff]', ' ', string_words, flags=re.IGNORECASE) # remove unicode (dash)
		string_words = re.sub(r'[\x80-\xff]', '', string_words, flags=re.IGNORECASE) # remove unicode
		file_remove_extra = string_words.split(' ')
		file_remove_extra = filter(None, file_remove_extra) # remove empty strings from list
	return file_remove_extra

def isDialogue(sentence):
	# return true/false if the value is a quote
	return '"' in sentence

def tokenizeSentence(string_sentence):
	'''EXAMPLE
	{60: 'After rather a long silence, the commander resumed the conversation.'}
	'''
	tokens_sentence_dict = {} # returns dict with {token location in text #: sentence}
	tokens_sent = string_sentence.split('.')

	index = 0
	for t in range(len(tokens_sent)):
		sent = tokens_sent[t].strip() # remove excess whitespace
		for dia in sent.split('~'):
			if dia != '': # store dialouge with its double quotes for identification
				tokens_sentence_dict[index] = dia # {4: '"Oh, why can\'t you remain like this for ever!"'}
				index += 1
				t += 1
	#print(tokens_sentence_dict)
	return tokens_sentence_dict

def partsOfSpeech(token_dict):
	'''EXAMPLE
	60: ('After rather a long silence, the commander resumed the conversation.', 
	[('After', 'IN'), ('rather', 'RB'), ('a', 'DT'), ('long', 'JJ'), ('silence', 'NN'),
	 (',', ','), ('the', 'DT'), ('commander', 'NN'), ('resumed', 'VBD'), ('the', 'DT'), 
	 ('conversation', 'NN'), ('.', '.')])}
	'''
	from subprocess import check_output
	import progressbar as pb
	widgets = ['Running POS tagger: ', pb.Percentage(), ' ', 
				pb.Bar(marker=pb.RotatingMarker()), ' ', pb.ETA()]
	timer = pb.ProgressBar(widgets=widgets, maxval=len(token_dict)).start()

	for i in range(len(token_dict)):
		timer.update(i)
		no_punc = token_dict[i].translate(None, string.punctuation) # remove puncuation from part of speech tagging
		pos_tagged = check_output(["./3_run_text.sh", token_dict[i]])
		if "docker not running, required to run syntaxnet" not in pos_tagged:
			pos_tagged = process_POS_conll(pos_tagged) # process conll output from shell
			token_dict[i] = (token_dict[i], pos_tagged) # adds part of speech tag for each word in the sentence
		else:
			print("\n\tWARNING: docker not running, cannot run syntaxnet for POS, exiting")
			exit()
	timer.finish()
	return token_dict

def process_POS_conll(conll_output):
	'''
	['1', 'At', '_', 'ADP', 'IN', '_', '13', 'prep', '_', '_']
	['2', 'the', '_', 'DET', 'DT', '_', '3', 'det', '_', '_']
	['3', 'period', '_', 'NOUN', 'NN', '_', '1', 'pobj', '_', '_']
	['4', 'when', '_', 'ADV', 'WRB', '_', '7', 'advmod', '_', '_']
	['5', 'these', '_', 'DET', 'DT', '_', '6', 'det', '_', '_']
	['6', 'events', '_', 'NOUN', 'NNS', '_', '7', 'nsubj', '_', '_']
	['7', 'took', '_', 'VERB', 'VBD', '_', '3', 'rcmod', '_', '_']
	['8', 'place', '_', 'NOUN', 'NN', '_', '7', 'dobj', '_', '_']
	'''
	pos_processed = conll_output
	#print(pos_processed)
	start_data = 0
	pos_processed = re.sub("\t", ",", pos_processed.strip())
	pos_processed = re.sub(",", " ", pos_processed.strip())
	pos_processed = pos_processed.splitlines()
	for i in range(len(pos_processed)):
		pos_processed[i] = pos_processed[i].split(" ")
		#print(pos_processed[i])
	return pos_processed

########################################################################
## GROUP PROPER NOUNS ENTITIES
def findProperNamedEntity(pos_dict):
	# returns {sentence index: [list of all proper nouns grouped]
	# {0: ["Scarlett O'Hara", 'Tarleton'], 1: ['Coast']}
	pos_type_lst = []
	# TODO: EXPAND PROPER NOUNS FOR COMMON WORDS AROUND WORD
	previous_nnp_index = 0
	for row, pos_named in pos_dict.iteritems():
		if "NNP" in pos_named.XPOSTAG: #"NN" in pos_named.XPOSTAG or "POS" in pos_named.XPOSTAG or "IN" in pos_named.XPOSTAG or "DT" in pos_named.XPOSTAG:
			pos_type_lst.append((int(pos_named.SENTENCE_INDEX), int(pos_named.ID), pos_named.FORM, int(pos_named.SENTENCE_LENGTH), pos_named.XPOSTAG))
			previous_nnp_index = int(pos_named.ID)
		if pos_named.FORM in connecting_words:
			pos_type_lst.append((int(pos_named.SENTENCE_INDEX), int(pos_named.ID), pos_named.FORM, int(pos_named.SENTENCE_LENGTH), pos_named.XPOSTAG))
			previous_nnp_index = int(pos_named.ID)
		#if "the" in pos_named.FORM or "The" in pos_named.FORM:
		#	if previous_nnp_index < int(pos_named.ID): # only store of if it is part of an existing sentence
		#		pos_type_lst.append((int(pos_named.SENTENCE_INDEX), int(pos_named.ID), pos_named.FORM, int(pos_named.SENTENCE_LENGTH), pos_named.XPOSTAG))
		#if "of" in pos_named.FORM:
		#	if previous_nnp_index < int(pos_named.ID): # only store of if it is part of an existing sentence
		#		pos_type_lst.append((int(pos_named.SENTENCE_INDEX), int(pos_named.ID), pos_named.FORM, int(pos_named.SENTENCE_LENGTH), pos_named.XPOSTAG))
		
	total_sentence_indices = list(set([i[0] for i in pos_type_lst]))

	sub_sentences = []
	for index in total_sentence_indices:
		# create sub sentences for each sentence [[0], [1])
		sub_sentences.append([x for x in pos_type_lst if x[0] == index])
	#print("\nsub_sentence={0}\n".format(sub_sentences))
	
	from operator import itemgetter # find sequences of consecutive values
	import itertools

	grouped_nouns = {}
	names_lst = []
	sentence_index = []
	for sentence in sub_sentences:
		noun_index = [s_index[1] for s_index in sentence] # noun location in a sentence (index)
		#print(sentence, noun_index)
		consec_lst = []
		for k, g in itertools.groupby(enumerate(noun_index), lambda x: x[1]-x[0]):
			consec_order = list(map(itemgetter(1), g))
			if len(consec_order) > 0: # if there is more than one noun in an order for a sentence
				consec_lst.append(consec_order)
		#consec_lst = [item for items in consec_lst for item in items]
		for c_l in consec_lst:
			g_name = [x for x in sentence if x[1] in c_l]
			nnp_in_sentence = False
			for i, v in enumerate(g_name):
				nnp_in_sentence = "NNP" in v
				if nnp_in_sentence: # if the nnp exist in the sub-list, exit and save
					break
			if nnp_in_sentence:
				#print(c_l)
				#print([x[2] for x in sentence if x[1] in c_l])
				#print(" ".join([x[2] for x in sentence if x[1] in c_l]))
				start_with_connecting_ignore = [x[2] for x in sentence if x[1] in c_l][0] in connecting_words
				end_with_connecting_ignore = [x[2] for x in sentence if x[1] in c_l][-1] in connecting_words
				if start_with_connecting_ignore or end_with_connecting_ignore:
				# if the gne starts with a connecting word, ignore the connecting name: 'of Divine Providence' -> 'Divine Providence'
					new_start_index = 0
					for first_words in [x[2] for x in sentence if x[1] in c_l]:
						if first_words not in connecting_words:
							break # if it doesn't start with a connecting word, ignore
						else:
							new_start_index += 1
					#print([x[2] for x in sentence if x[1] in c_l][new_start_index:])
					#print(" ".join([x[2] for x in sentence if x[1] in c_l][new_start_index:]))
					new_end_index = len([x[2] for x in sentence if x[1] in c_l]) # last element after it is been updated
					for last_words in reversed([x[2] for x in sentence if x[1] in c_l]):
					# if the gne ends with a connecting word, ignore the connecting name: 'Tom of the' -> 'Tom'
						if last_words not in connecting_words:
							break
						else:
							new_end_index -= 1
					#if new_end_index <  len([x[2] for x in sentence if x[1] in c_l]):
					#	print("original: {0}".format(" ".join([x[2] for x in sentence if x[1] in c_l])))
					#	print("update: {0}\n".format(" ".join([x[2] for x in sentence if x[1] in c_l][new_start_index:new_end_index])))
					#	print(new_start_index, new_end_index)
					if (new_end_index != 0) and (new_start_index != len([x[2] for x in sentence if x[1] in c_l])): # if the entire gne wasn't connecting words
						names_lst.append(" ".join([x[2] for x in sentence if x[1] in c_l][new_start_index:new_end_index]))
						sentence_index.append(list(set([x[0] for x in sentence if x[1] in c_l][new_start_index:new_end_index]))[0])
				else:
					names_lst.append(" ".join([x[2] for x in sentence if x[1] in c_l]))
					sentence_index.append(list(set([x[0] for x in sentence if x[1] in c_l]))[0])

	dic_tmp = zip(sentence_index, names_lst)
	grouped_nouns = defaultdict(list)
	for s, n in dic_tmp:
		grouped_nouns[s].append(n)
	return dict(grouped_nouns)

def commonSurrouding(grouped_nouns_dict):
	# find the most common preceding words to append
	pass

def groupSimilarEntities(grouped_nouns_dict):
	# filter out enities that only appear once and re-organize
	'''
	[['America'], ['Aronnax', 'Pierre', 'Pierre Aronnax'],
	['Captain Farragut', 'Captain', 'Farragut'], ['Conseil'], 
	['English'], ['Europe'], ['French'], ['Gentlemen'], ['God'], 
	['Land', 'Mr Ned Land', 'Ned', 'Ned Land'], ['Latin'],
	['Lincoln', 'Abraham', 'Abraham Lincoln'], ['Museum'], 
	['Natural'], ['OEdiphus'], ['Pacific'], ['Paris'], ['Professor'],
	['Sir'], ['Sphinx'], ['United States', 'States', 'United'],
	['sir']]
	'''
	counter_dict = dict(Counter([val for sublist in grouped_nouns_dict.values() for val in sublist]))

	#print("counter={0}".format(counter_dict))

	names_all = list(set([val for sublist in grouped_nouns_dict.values() for val in sublist])) # is a list of all unquie names in the list
	compare_names_same_format = [val.upper() for val in names_all]
	# loop through to group similar elements
	gne_list_of_lists = grouped_nouns_dict.values()
	gne_list_of_lists = list(set([item for sublist in gne_list_of_lists for item in sublist])) # creates a list of unquie names

	import difflib 
	from difflib import SequenceMatcher
	gne_name_group = []
	# find most similar ['Professor', 'Professor Aronnax'], ['Aronnax', 'Mr Aronnax', 'Pierre Aronnax']
	for gne in gne_list_of_lists:
		for g in gne.split():
			compared = difflib.get_close_matches(g, gne_list_of_lists)
			if compared != []:
				gne_name_group.append(compared)

	subgrouping = []
	#print("\ngne_list_of_lists: {0}".format(gne_list_of_lists))
	if len(gne_list_of_lists) > 1: # if there is only one name in all the text (debugging short texts)
		for gne in gne_list_of_lists:
			sublist = []
			if len(gne.split()) == 1 and len(gne.split()[0]) > 1: # includes only single instance values that are not a single letter
				sublist.append(gne.split()) # include values that only appear once in a setence
			for i in gne.split():
				for gne_2 in gne_list_of_lists:
					if i in gne_2 and i != gne_2 and (i != [] or gne_2 != []):
						chapter_titles = ["CHAPTER", "Chapter", "Volume", "VOLUME"]
						# only save words that don't include the chapter titles
						found_in_i = any(val in chapter_titles for val in i.split())
						found_in_gne2 = any(val in chapter_titles for val in gne_2.split())
						if found_in_i or found_in_gne2:
							# 'CHAPTER XXII Mr Rochester' -> 'Mr Rochester'
							for title in chapter_titles:
								if found_in_i:
									#print(" ".join(i.split()[2:]))
									i = " ".join(i.split()[2:])
									break
								if found_in_gne2:
									#print(" ".join(gne_2.split()[2:]))
									gne_2 = " ".join(gne_2.split()[2:])
									break
							if i != '' and gne_2 != '':
								#print("FINAL APPEND={0}\n".format((i, gne_2)))
								sublist.append([i, gne_2])
					else:
						if gne_2 != i:
							if gne_2 not in i:
								if [gne_2] not in sublist: # only keep one iteration of the name
									if len(gne_2) > 1: # exclude single letter
										sublist.append([gne_2])
			subgrouping.append(sublist)
	else:
		subgrouping.append(gne_list_of_lists)

	final_grouping = []
	if len(subgrouping) > 1:
		subgrouping = [x for x in subgrouping if x != []]
		for subgroup in subgrouping:
			final_grouping.append(list(set([item for sublist in subgroup for item in sublist])))
	else:
		final_grouping = subgrouping # keep the single element

	iterate_list_num = list(range(len(final_grouping)))
	for i in range(len(final_grouping)):
		for num in iterate_list_num:
			if num != i:
				extend_val = list(set(final_grouping[i]).intersection(final_grouping[num]))
				if extend_val:
					final_grouping[i].extend(final_grouping[num])
					final_grouping[i] = sorted(list(set(final_grouping[i]))) # extend list to include similar elements

	#print("\nfinal_grouping: {0}".format(final_grouping))

	final_grouping = sorted(final_grouping) # organize and sort
	final_grouping = list(final_grouping for final_grouping,_ in itertools.groupby(final_grouping))

	#print([item for item in final_grouping if item not in words_to_ignore])
	count = 0
	character_group_list = []
	# remove any word that is part of the 'words_to_ignore' list
	for item in final_grouping:
		sublist = []
		for i in item:
			if i in words_to_ignore:
				count += 1
				#print("in word to ignore = {0}".format(i))
			else:
				#print(i)
				sublist.append(i)
		#print("item = {0}".format(item))
		if item[0] in words_to_ignore:
			count += 1
			if item[0] in words_to_ignore:
				pass#print("in word to ignore = {0}".format(item[0]))
			else:
				#print(item[0])
				sublist.append(item[0])
		if sublist != []:
			character_group_list.append(sublist)
	#print("character_group_list: {0}".format(character_group_list))

	character_group = [] # only save unquie lists
	for i in character_group_list:
		if i not in character_group:
			character_group.append(i)

	#print("\nfinal group: \n{0}".format(final_grouping))
	#print("\ncharacter group: \n{0}".format(character_group))
	#print(len([item for item in final_grouping if item not in words_to_ignore]))
	#print(len(final_grouping))
	#print(len(character_group))
	#print("count = {0}".format(count))
	#print(words_to_ignore)
	return character_group

def lookupSubDictionary(shared_ent):
	# return a dictionary of proper nouns and surrounding values for one-shot look up
	'''
	{"Scarlett O'Hara": ["O'Hara", 'Scarlett'], 'Tarleton': ['Tarleton'], 
	"O'Hara": ["Scarlett O'Hara", 'Scarlett'], 'Scarlett': ["Scarlett O'Hara", "O'Hara"],
	 'Coast': ['Coast']}
	'''
	sub_dictionary_lookup = defaultdict(list)
	for group in shared_ent:
		iterate_list_num = list(range(len(group)))
		for i in range(len(group)):
			for j in iterate_list_num:
				if i != j:
					sub_dictionary_lookup[group[i]].append(group[j])
		if len(group) == 1:
			sub_dictionary_lookup[group[i]].append(group[i]) # for single instances, store {'Tarleton':'Tarleton'{ as its own reference

	return dict(sub_dictionary_lookup)

def mostCommonGNE(gne_grouped_dict):
	# find the longest most common version of a name in gnes to become the global
	#print("\nGlobal GNE")
	#for key, value in gne_grouped_dict.iteritems():
	#	print(key, value)
	#print(gne_grouped_dict.values())
	pass
	
########################################################################
## INDEX PRONOUNS
def findPronouns(pos_dict):
	# return the sentence index and pronouns for each sentence
	#{0: ['he', 'himself', 'his'], 1: ['He', 'his', 'he', 'his', 'he', 'his']}
	pos_type_lst = []
	for row, pos_named in pos_dict.iteritems():
		if "PRP" in pos_named.XPOSTAG:
			pos_type_lst.append((int(pos_named.SENTENCE_INDEX), int(pos_named.ID), pos_named.FORM, int(pos_named.SENTENCE_LENGTH), pos_named.XPOSTAG))

	total_sentence_indices = list(set([i[0] for i in pos_type_lst]))
	sub_sentences = []
	for index in total_sentence_indices:
		# create sub sentences for each sentence [[0], [1])
		sub_sentences.append([x for x in pos_type_lst if x[0] == index])

	grouped_pronouns = 	{}
	for pronoun_group in sub_sentences:
		pronoun_lst = []
		for pronoun in pronoun_group:
			pronoun_lst.append(pronoun[2])
		grouped_pronouns[pronoun[0]] = pronoun_lst

	return grouped_pronouns

def coreferenceLabels(filename, csv_file, character_entities_dict, global_ent, pos_dict):
	# save into csv for manual labelling
	# TODO: set up with average paragraph length as size_sentences
	size_sentences = 21000000000 # looking at x sentences at a time (could be automatically re-adjusted to fix max size of text)
	rows_of_csv_tuple = csv_file.values()
	all_sentences_in_csv = list(set([int(word.SENTENCE_INDEX) for word in csv_file.values()]))
	if size_sentences > max(all_sentences_in_csv)+1: # do not go out of range while creating sentences
		size_sentences = max(all_sentences_in_csv)+1
	print("Size of sentence for manual tagging = {0}".format(size_sentences))
	
	# save chucks of text (size sentences = how many sentences in each chunk of text)
	sub_sentences_to_tag = [all_sentences_in_csv[i:i + size_sentences] for i in xrange(0, len(all_sentences_in_csv), size_sentences)]
	#print("character entities keys: {0}\n".format(character_entities_dict.keys()))
	
	#print("\n")
	row_dict = {} # to print data into csv
	gne_index = 0 # display word of interst as [Name]_index
	pronoun_index = 0 # display word of interst as [Pronoun]_index
	for sentences_tag in sub_sentences_to_tag:
		#print(sentences_tag)
		if len(sentences_tag) == size_sentences: # ignores sentences at the end that aren't the right length
			sentences_in_order = ''
			for i in range(sentences_tag[0], sentences_tag[-1]+1):
				new_sentence_to_add = list(set([row.SENTENCE for row in rows_of_csv_tuple if row.SENTENCE_INDEX == str(i)]))[0]
				if i+1 < sentences_tag[-1]+1:
					next_sentence_check = list(set([row.SENTENCE for row in rows_of_csv_tuple if row.SENTENCE_INDEX == str(i+1)]))[0]
					if len(next_sentence_check) == 1:
						#print("old: {0}".format(new_sentence_to_add))
						#print("NEXT IS NEARLY EMPTY, APPEND TO PREVIOUS SENTENCE: '{0}'".format(next_sentence_check))
						new_sentence_to_add += next_sentence_check # add the final dialouge tag into the previous sentence
						#print("new: {0}".format(new_sentence_to_add))
				# returns a sentence in range
				new_sentence_to_add = " {0} ".format(new_sentence_to_add) # add whitespace to the begining to find pronouns that start a sentence
				if "," in new_sentence_to_add:
					new_sentence_to_add = new_sentence_to_add.replace(",", " , ")
				if "\"" in new_sentence_to_add:
					new_sentence_to_add = new_sentence_to_add.replace("\"", " \" ")
				# add space to identify pronouns/nouns at the end of a sentence
				if "!" in new_sentence_to_add:
					new_sentence_to_add = new_sentence_to_add.replace("!", " ! ")
				if "?" in new_sentence_to_add:
					new_sentence_to_add = new_sentence_to_add.replace("?", " ? ")


				# tag pronouns first (from pos_dict)
				if i in pos_dict.keys():
					for pronoun in pos_dict[i]: # for all pronouns within the given sentence
						total_found = re.findall(r'\b{0}\b'.format(pronoun), new_sentence_to_add)
						if re.search(r' \b{0}\b '.format(pronoun), new_sentence_to_add): # match full word
							for tf in range(len(total_found)):
								new_sentence_to_add = new_sentence_to_add.replace(" {0} ".format(pronoun), " <{0}>_p{1} ".format(pronoun, pronoun_index), tf+1)
								pronoun_index += 1
	
				#TODO: FIND PRONOUNS/PROPER NAMES close to puncation: what do you make of it? don't do it!

				# tag proper nouns
				found_longest_match = ''
				gne_found_in_sentence = False # if found, print and update the sentence value
				
				lst_gne = []
				lst_gne = [gne_name for gne_name in character_entities_dict.keys() if gne_name in new_sentence_to_add]
				lst_gne = [x for x in lst_gne if x != []]

				index_range_list = [] # compare each index values
				all_index_values = [] # contains all index values of gnes
				to_remove = [] # if a value is encompassed, it should be removed

				if len(lst_gne) > 0:
					#print("\nlst_gne = {0}".format(lst_gne))
					for gne in lst_gne: # create the index values for each enitity
						#print("{0}".format(new_sentence_to_add))
						search_item = re.search(r"\b{0}\b".format(gne), new_sentence_to_add)
						if not search_item: # if it return none
							break # skip item if not found
						else:
							start = search_item.start() # store the start index of the gne
							end = search_item.end() # store the end index of the gne
						index_range_word = [start, end]
						all_index_values.append(index_range_word)
						if len(index_range_list) == 0: # useful for debugging
							#print("FIRST GNE {0} has index {1}".format(gne, index_range_word))
							pass
						else:
							for range_index in index_range_list: # the index of the value is stored and new words are check to see if they are contained wtihing
								# example: united is within 'united states'
								if len(lst_gne) > 1:
									if (range_index[0] == index_range_word[0]) and (index_range_word[1] == range_index[1]):
										pass
									else:
										if (range_index[0] <= index_range_word[0]) and (index_range_word[1] <= range_index[1]):
												#print("{0} <= {1}-{2} <= {3}".format(range_index[0], index_range_word[0], index_range_word[1], range_index[1]))
												#print("{0} IS CONTAINED BY GNE = {1}\n".format(gne, new_sentence_to_add[range_index[0]:range_index[1]]))
												to_remove.append(index_range_word)
										if (index_range_word[0] <= range_index[0]) and(index_range_word[1] >= range_index[1]):
												#pass # reprsents the larger word that encompassing the smaller word
												#print("{0} <= {1}-{2} <= {3}".format(index_range_word[0], range_index[0],range_index[1], index_range_word[1]))
												#print("{0} IS EMCOMPASSED BY GNE = {1}\n".format(gne, new_sentence_to_add[index_range_word[0]:index_range_word[1]]))
												to_remove.append(range_index)
												#print("{0} <= {1} = {2}".format(index_range_word[0], range_index[0], index_range_word[0] <= range_index[0]))
												#print("{0} >= {1} = {2}".format(index_range_word[1], range_index[1], index_range_word[1] >= range_index[1]))
						index_range_list.append(index_range_word)
					#print("remove index values = {0}".format(to_remove))
					#print("largest gne index values ALL = {0}".format(all_index_values))
					all_index_values = sorted([x for x in all_index_values if x not in to_remove]) # index in order based on start value
					#print("shared (with removed encompassed) = {0}".format(all_index_values)) # remove all encompassed elements

					updated_index = []
					new_characters_from_update = 0 # new characters to keep track of character length when indexing
					repeats_to_find = []
					for counter, index_val in enumerate(all_index_values):
						if counter > 0:
							new_characters_from_update = len("<>_n ")*counter
						start_word = index_val[0] + new_characters_from_update
						end_word = index_val[1] + new_characters_from_update
						updated_index.append([start_word, end_word])
						find_repeats = new_sentence_to_add[start_word:end_word]
						repeats_to_find.append(find_repeats)
						replacement_string = "<{0}>_n ".format(new_sentence_to_add[start_word:end_word])
						new_sentence_to_add = "".join((new_sentence_to_add[:start_word], replacement_string, new_sentence_to_add[end_word:]))
						sub_counter = counter
					# add repeated gne values
					# if the same name appears more than once in a sentence 
					sub_counter = 0
					new_characters_from_update = 0 # new characters to keep track of character length when indexing
					for find_additional in repeats_to_find:
						repeat_item = re.finditer(r"\b{0}\b".format(find_additional), new_sentence_to_add)
						for m in repeat_item:
							index_to_check = [m.start(), m.end()]
							if [m.start()-1,m.end()-1] not in updated_index: # check that name hasn't been already assigned
								if new_sentence_to_add[m.start()-1] != '<' and new_sentence_to_add[m.end():m.end()+3] != '>_n':
									start_word = m.start() + new_characters_from_update
									end_word = m.end() + new_characters_from_update
									replacement_string = "<{0}>_n ".format(new_sentence_to_add[start_word:end_word])
									new_sentence_to_add = "".join((new_sentence_to_add[:start_word], replacement_string, new_sentence_to_add[end_word:]))
									sub_counter += 1
				new_sent = new_sentence_to_add.split()
				# label all proper nouns with an associated index value for noun
				for index, word_string in enumerate(new_sent):
					if '>_n' in word_string:
						if word_string != ">_n":
							new_sent[index] = '{0}{1}'.format(word_string, gne_index)
							new_sentence_to_add = " ".join(new_sent)
							gne_index += 1
				new_sentence_to_add = new_sentence_to_add.strip() # remove precending whitespace
				new_sentence_to_add = new_sentence_to_add.replace('" ', '"') # edit the speech puncutations
				new_sentence_to_add = new_sentence_to_add.replace(' "', '"') # edit the speech puncutations
				new_sentence_to_add = new_sentence_to_add.replace('\' ', '\'') # edit the speech puncutations
				new_sentence_to_add = new_sentence_to_add.replace(' , ', ', ') # edit the speech puncutations
				new_sentence_to_add = new_sentence_to_add.replace(' ! ', '! ') # edit the speech puncutations
				new_sentence_to_add = new_sentence_to_add.replace(' ? ', '? ') # edit the speech puncutations
				if new_sentence_to_add != '"': # if the value is just the end of a dialouge tag (already included, ignore)
					sentences_in_order += new_sentence_to_add + '. '
					#print(new_sentence_to_add + '. ')
			#print("\nFinal Sentence Format:\n\n{0}".format(sentences_in_order))
			saveTagforManualAccuracy(sentences_in_order)

def saveTagforManualAccuracy(sentences_in_order):
	## corefernece will call the csv creator for each 'paragraph' of text
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "manualTagging_{0}.csv".format(given_file.upper())

	fieldnames = ['FILENAME', 'TEXT',
				  'FOUND_PROPER_NOUN', 'MISSED_PROPER_NOUN',
				  'FOUND_PRONOUN', 'MISSED_PRONOUN']

	split_sentences_in_list = [e+'.' for e in sentences_in_order.split('.') if e] # split sentence based on periods
	split_sentences_in_list.remove(' .') # remove empty sentences
	sentence_size = 21000000000 # size of the sentence/paragraph saved in manual tagging
	sentence_range = [split_sentences_in_list[i:i+sentence_size] for i in xrange(0, len(split_sentences_in_list), sentence_size)]
	# range stores the sentences in list of list based on the size of tag

	#print("\n")
	#for sentence_tag in sentence_range:
	#	print(''.join(sentence_tag))
	#	print(''.join(sentence_tag).count("]_n"))
	#	print(''.join(sentence_tag).count("]_p"))
	#	print("\n")

	with open('manual_tagging/{0}'.format(output_filename), 'w') as tag_data:
		writer = csv.DictWriter(tag_data, fieldnames=fieldnames)
		writer.writeheader() 
		# leave MISSED empty for manual tagging
		for sentence_tag in sentence_range:
			writer.writerow({'FILENAME': os.path.basename(os.path.splitext(filename)[0]), 
							 'TEXT': ''.join(sentence_tag),
							 'FOUND_PROPER_NOUN': ''.join(sentence_tag).count(">_n"),
							 'MISSED_PROPER_NOUN': None,
							 'FOUND_PRONOUN': ''.join(sentence_tag).count(">_p"),
							 'MISSED_PRONOUN': None 
							})
	print("{0} create MANUAL TAGGING for CSV".format(output_filename))

def coreferenceResolution(manual_tag_dir, gender_gne_tree, loaded_gender_model):
	# find all locations of character interactions
	print("\nFIND INTERACTIONS in {0}\n".format(manual_tag_dir))
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	
	neutral_pronouns = ['I', 'Me', 'You', 'It', 'We', 'Us', 'They', 'Them', 'Myself',
						'Yourself', 'Itself', 'Themselves', 'My', 'Your', 'Its', 'Our', 'Their']
	female_pronouns = ['Her', 'Herself', "She", 'Herself']
	male_pronouns =   ['He', 'Him', 'His', 'Himself']
	pronoun_gender = {f: 'Female' for f in female_pronouns}
	m_pronoun_gender = {m: 'Male' for m in male_pronouns}
	pronoun_gender.update(m_pronoun_gender)
	n_pronoun_gender = {n: 'Neutral' for n in neutral_pronouns}
	pronoun_gender.update(n_pronoun_gender)
	
	#check that all pronouns have been included in the dictionary
	test_full_list = female_pronouns + male_pronouns + neutral_pronouns
	for i in test_full_list:
		if i not in pronoun_gender:
			print("'{0}' NOT FOUND IN GENDER DICT".format(i))
	
	tagged_text = [] # store old rows
	with open(manual_tag_dir, 'r') as tag_data:
		reader = csv.reader(tag_data)
		next(reader) # skip header
		for row in reader:
			tagged_text.append(row[1]) # store the sentence in order

	total_sentences_to_check_behind = 3 # TODO: update with pronouns average information

	for row in tagged_text:
		print(row)
		find_gne_in_sentence_pattern = r'(?<=\<)(.*?)(?=\>)'
		found_all_brackets = re.findall(find_gne_in_sentence_pattern, row) # everything together in the order that they appear
		print('\n')
		print(found_all_brackets)
		all_found_name_index = [[m.start(), m.end()] for m in re.finditer(find_gne_in_sentence_pattern, row)] # get index of all matches
		found_proper_name_value = [row[i[0]:i[1]] for i in all_found_name_index if row[i[1]+2] is 'n'] # store named ents
		found_proper_name_index = [i for i in all_found_name_index if row[i[1]+2] is 'n'] # store named index of names
		#for index_g in all_found_name_index:
		#	print(row[index_g[0]:index_g[1]])
		found_pronoun_value = [row[i[0]:i[1]] for i in all_found_name_index if row[i[1]+2] is 'p'] # store pronouns seperately
		found_pronoun_index = [i for i in all_found_name_index if row[i[1]+2] is 'p'] # store named index of pronouns
		#print("\nfound pronouns index: {0}".format(all_found_name_index))
		#for index_g in all_found_name_index:
		#	print(row[index_g[0]:index_g[1]])
		for given_name in found_proper_name_value:
			given_name_gender = gender_gne_tree[given_name]
			print("{0} is {1}".format(given_name, given_name_gender))
			#given_name_index = [index for index, value in enumerate(found_all_brackets) if value == given_name]
			#for index_name in given_name_index:
			#	print(found_all_brackets[index_name:])
			#print("\n")
			#most_common_pronoun_dict[given_name] = mostCommonSurroudingPronouns(given_name, found_all_brackets, found_name_value, found_pronoun_value)
			#print(found_all_brackets)
		print('\n')
		print(found_pronoun_value)
		for pron in found_pronoun_value:
			print("{0} is {1}".format(pron, pronoun_gender[pron.capitalize()]))



def determineGenderName(loaded_gender_model, gne_tree):
	# use trained model to determine the likely gender of a name
	gender_gne = {}
	
	all_gne_values =  gne_tree.keys()
	for key, values in gne_tree.iteritems():
		for k, v in values.iteritems():
			# add all sub_trees to list
			all_gne_values += [k]
			all_gne_values += v

	for full_name in all_gne_values:
		found_with_title = False
		female_prob = 0.0
		male_prob = 0.0

		full_name_in_parts = full_name.split()
		
		# if name is part of a gendered honorific, return: Mr Anything is a male
		if full_name_in_parts[0].title() in male_honorific_titles:
			#print("'{0}' contains '{1}' found: Male".format(full_name, full_name_in_parts[0]))
			gender_is = 'Male'
			male_prob += 1.0
			found_with_title = True
		if full_name_in_parts[0].title() in female_honorific_titles:
			#print("'{0}' contains '{1}' found: Female".format(full_name, full_name_in_parts[0]))
			gender_is = 'Female'
			female_prob += 1.0
			found_with_title = True
		
		# find the name for each part of the name, choose highest
		#print("'{0}' not found, calculating a probability...".format(full_name)) # not found in gendered honorifics
		# run test on each part of the name, return the largest so that last names don't overly effect
		dt = np.vectorize(DT_features) #vectorize dt_features function

		weight_last_name_less = 0.3
		
		if not found_with_title:
			for sub_name in full_name_in_parts:
				# determine if the name is likely to be the last name, if so, weight less than other parts of the name
				if sub_name in connecting_words:
					# do not calculate for titles "Queen of England" shouldn't find for England
					break
				else:
					if sub_name not in ignore_neutral_titles:
						# female [0], male [1]
						is_a_last_name = isLastName(gne_tree, sub_name)
						load_prob = loaded_gender_model.predict_proba(dt([sub_name.title()]))[0]
						#print("\tprobability: {0}\n".format(load_prob))
						if is_a_last_name: # if last name, weigh less than other names
							#print("'{0}' is a last name, will weight less".format(sub_name))
							load_prob = load_prob*weight_last_name_less
						female_prob += load_prob[0]
						male_prob += load_prob[1]
				#print("\t  updated: f={0}, m={1}".format(female_prob, male_prob))

			if (abs(male_prob - female_prob) < 0.02): #within 2 percent, undeterminex
				gender_is = "UNDETERMINED"
			else:
				gender_is = 'Male' if male_prob > female_prob else 'Female'

		#print("The name '{0}' is most likely {1}\nFemale: {2:.5f}, Male: {3:.5f}\n".format(full_name, gender_is, female_prob, male_prob))
		gender_gne[full_name] = gender_is
	return gender_gne

def isLastName(gne_tree, sub_name):
	# determine if the name is likely to be the last name
	#{'Samsa': ['Samsa'], 'Gregor': ['Gregor', 'Gregor Samsa']}
	# last name is the most common last element in a name and has no futher sub-roots
	# last name will be weighted less, if there are other elements present
	is_last_name = False

	for key, value in gne_tree.iteritems():
		if sub_name in key:
			if sub_name in key.split()[-1] and len(value) > 1: # if in the last position and isn't the only value {'John': ['John']}
				is_last_name = True
	#print("'{0}' is a last name = {1}".format(sub_name, is_last_name))
	return is_last_name

def loadDTModel():
	# load saved gender model from gender_name_tagger
	from sklearn.externals import joblib # save model to load
	model_file_dir = 'gender_name_tagger'
	updated_saved_model = [f for f in os.listdir(model_file_dir) if 'pipeline_gender_saved_model' in f][0]
	print("LOADING SAVED GENDER NAME MODEL: {0}".format(updated_saved_model))
	pipeline_loaded = joblib.load('{0}/{1}'.format(model_file_dir, updated_saved_model))
	return pipeline_loaded

def DT_features(given_name):
	test_given_name = ['corette', 'corey', 'cori', 'corinne', 'william', 'mason', 'jacob', 'zorro'] #small test
	FEATURE_TAGS = ['first_letter', 
				'first_2_letters',
				'first_half',
				'last_half',
				'last_2_letters',
				'last_letter',
				 'length_of_name']
	features_list = []
	name_features = [given_name[0], given_name[:2], given_name[:len(given_name)/2], given_name[len(given_name)/2:], given_name[-2:], given_name[-1:], len(given_name)]
	#[['z', 'zo', 'zo', 'rro', 'ro', 'o', 5], ['z', 'zo', 'zo', 'rro', 'ro', 'o', 5]]
	features_list = dict(zip(FEATURE_TAGS, name_features))
	return features_list

def gneHierarchy(character_entities_group):
	# merge gne into a dict for look up
	'''
	key: Dr Urbino
	{'Dr': [['Dr', 'Dr Juvenal Urbino', 'Dr Urbino'], ['Urbino']], 
	'Urbino': [['Dr', 'Dr Juvenal Urbino', 'Dr Urbino'], ['Urbino']]}
	 '''
	character_split_group = [x.split() for x in character_entities_group]
	character_split_group = sorted(character_split_group, key=len, reverse=True)
	gne_tree = defaultdict(dict)
	gne_dict_sub = {}

	all_honorific_titles = female_honorific_titles + male_honorific_titles + ignore_neutral_titles

	for longer_name in character_split_group:
		#print("{0} IS NOT in gne_tree: {1}".format(" ".join(longer_name), gne_tree))
		#print("longer: {0}".format(longer_name))
		already_in_tree = any(" ".join(longer_name) in g for g in gne_tree)
		if not already_in_tree: # if not already in a sub tree
			if len(longer_name[0]) > 1: # ignore intials 'C'
				#print("base: {0}".format(longer_name))
				#print("base: {0}".format(" ".join(longer_name)))
				#gne_tree_sub_tree.append(smaller_name)
				for sub_long_name in longer_name:
					gne_tree_word_tree = []
					#print("sub: {0}".format(sub_long_name))
					gne_tree_word_tree.append(sub_long_name)
					for smaller_name in character_entities_group:
						name_with_caps = sub_long_name
						is_sub_capitalized = sub_long_name.isupper()
						if is_sub_capitalized:
							name_with_caps = sub_long_name.title()
						if name_with_caps in smaller_name.split() and name_with_caps not in connecting_words:
							# store only honorific titles that include elements of the same name
							# 'Dr Juvenal Urbino' NOT 'Dr Lacides Olivella', but 'Dr Juvenal Urbino' and 'Dr Urbino' 
							if name_with_caps in all_honorific_titles and len(longer_name) > 1:
								if any(i.title() in longer_name for i in smaller_name.split() if i.title() not in all_honorific_titles):
									#print("\t\tindex: {0}".format(smaller_name.split().index(sub_long_name)))
									sub_name_join = " ".join(smaller_name.split()[smaller_name.split().index(sub_long_name):])
									#print("\t\t\n\n\nnewfound: {0}".format(sub_name_join))
									if sub_name_join.title() not in gne_tree_word_tree:
										gne_tree_word_tree.append(sub_name_join)
							else:
								if name_with_caps not in connecting_words:
									# save non-caps version of a name
									sub_name_join = " ".join(smaller_name.split()[smaller_name.split().index(name_with_caps):])
									#print("\t\tsub orig: {0}".format(sub_long_name))
									#print("\t\tnewfound: {0}\n".format(sub_name_join.upper()))
									if sub_name_join not in gne_tree_word_tree:
										gne_tree_word_tree.append(sub_name_join)
					#print("\ttotal found: {0}".format(gne_tree_word_tree))
					#print("NEW DICT ITEM {0}:{1}".format(sub_long_name, gne_tree_word_tree))
					if sub_long_name not in connecting_words:
						gne_tree[" ".join(longer_name)][sub_long_name] = gne_tree_word_tree
					gne_tree_word_tree = []

	#for key, value in gne_tree.iteritems():
	#	print("key: {0}".format(key))
	#	print(value)
	#	print("\n")
	return dict(gne_tree)

def mostCommonSurroudingPronouns(given_name, found_all_brackets, found_name_value, found_pronoun_value):
	# determine the most common pronouns for a given name for all the text
	'''
	x_closest_pronouns = 5
	print("MOST COMMON PRONOUN IN ALL TEXT FOR '{0}'".format(given_name))
	print(found_all_brackets)
	given_name_index = [index for index, value in enumerate(found_all_brackets) if value == given_name]
	for index_name in given_name_index:
		print("\n")
		print(found_all_brackets[index_name])
		search_list = []
		print("remaining list: {0}".format(found_all_brackets[index_name+1:]))
		for i in found_all_brackets[index_name+1:]:
			if i not in found_name_value:
				if len(search_list) < x_closest_pronouns:
					search_list.append(i)
		print(search_list)
	print("\n")
	'''
	
########################################################################
# NETWORK GRAPHS AND TREE
def generateGNEtree(gne_tree, filename):
	print("\nGENERATE TREE FROM GNE")
	import pygraphviz
	from networkx.drawing.nx_agraph import graphviz_layout


	gne_imge_directory_name = os.path.splitext(filename)[0].upper()
	if not os.path.exists("gne_trees/{0}".format(gne_imge_directory_name)):
		os.makedirs("gne_trees/{0}".format(gne_imge_directory_name))
	for key, value in gne_tree.iteritems():
		print("\ngne base name: {0}\n{1}".format(key, value))
	
	for key, value in gne_tree.iteritems():
		G = nx.DiGraph(name="GNE name tree: {0}".format(key))
		G.add_node(key) # root is the gne base name (Dr Juvenal Urbino)
		
		# add child (the name broken into parts)
		for split_name in key.split():
			G.add_edge(key, split_name)
		#for sub_name in value:
		#	print(sub_name)
		#G.add_edge(key, 
	
		nx.nx_pydot.write_dot(G, 'gne_trees/{0}/{1}.dot'.format(gne_imge_directory_name, key.replace(" ", "_")))
		plt.title("GNE name tree: {0}".format(key))
		pos=nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
		nx.draw(G, pos, with_labels=True, arrows=False, node_size=1600, cmap=plt.cm.Blues, node_color=range(len(G)))
		#nx.draw(G, with_labels=False, arrows=False)
		plt.savefig("gne_trees/{0}/GNE_{1}.png".format(gne_imge_directory_name, key.replace(" ", "_")))

def networkGraphs(gne_tree):
	print("\ngenerating network graphs of interactions")

	gne_labels = {} # set up same color for names in the same gne tree

	fig = plt.figure()
	fig.set_figheight(10)
	fig.set_figwidth(10)
	import graphviz

	G = nx.MultiGraph(name="Testing graph")

	for key, value in gne_tree.iteritems():
		print(key)
		G.add_node(key)
		for value_lst in value[0]:
			for v in value_lst:
				if v not in connecting_words:
					print(v)
					c = 'r'
					print(len(v))
					G.add_edge(key, v, color='red')
					#if len(v) > 10:
					#	G.add_edge(key, v) # add a second edge
		print("\n")

	print(nx.info(G))
	print("density={0}".format(nx.density(G)))
	for node in nx.degree(G):
		print("{0} has {1} connections".format(node[0], node[1]))
	nx.draw(G, with_labels=True, cmap=plt.cm.Blues, node_color=range(len(G)), node_size=2300)
	print("\n")
	plt.savefig("relationships_gne.png")
	print("finished generating graph")
	'''
	G=nx.star_graph(20)
	pos=nx.spring_layout(G)
	colors=range(20)
	nx.draw(G,pos,node_color='#A0CBE2',edge_color=colors,width=4,edge_cmap=plt.cm.Blues,with_labels=False)

	G=nx.random_geometric_graph(200,0.125)
	# position is stored as node attribute data for random_geometric_graph
	pos=nx.get_node_attributes(G,'pos')

	# find node near center (0.5,0.5)
	dmin=1
	ncenter=0
	for n in pos:
		x,y=pos[n]
		d=(x-0.5)**2+(y-0.5)**2
		if d<dmin:
			ncenter=n
			dmin=d

	# color by path length from node near center
	p=nx.single_source_shortest_path_length(G,ncenter)

	plt.figure(figsize=(8,8))
	nx.draw_networkx_edges(G,pos,nodelist=[ncenter],alpha=0.4)
	nx.draw_networkx_nodes(G,pos,nodelist=p.keys(),
						   node_size=80,
						   node_color=p.values(),
						   cmap=plt.cm.Reds_r)

	plt.xlim(-0.05,1.05)
	plt.ylim(-0.05,1.05)
	plt.axis('off')
	'''
	
########################################################################
# DATA ANAYLSIS
def percentagePos(total_words, csv_dict):
	# prints the percentage of the text that is pronouns vs. nouns
	percentageDict =  {}
        #TODO: finish percentages dictionary to pass into the csv and store if filename is new/modified
	pronouns_count = [pos.XPOSTAG for _, pos in csv_dict.iteritems()].count("PRP")
	pronoun_percentage = float(pronouns_count)/float(total_words)
	print("\npercent pronouns = {0:.3f}% of all text".format(pronoun_percentage*100.0))
	percentageDict['pronoun_in_all_words'] = pronoun_percentage

	proper_nouns_count = [pos.XPOSTAG for _, pos in csv_dict.iteritems()].count("NNP") # proper noun singular
	proper_nouns_count += [pos.XPOSTAG for _, pos in csv_dict.iteritems()].count("NNPS") # proper noun plural: spaniards
	proper_nouns_percentage = float(proper_nouns_count) / float(total_words)
	print("percent proper nouns = {0:.3f}% of all text".format(proper_nouns_percentage*100))
	percentageDict['proper_noun_in_all_words'] = proper_nouns_percentage

	nouns_count = [pos.XPOSTAG for _, pos in csv_dict.iteritems()].count("NN") # nouns: ship, language
	nouns_count += [pos.XPOSTAG for _, pos in csv_dict.iteritems()].count("NNS") # plurla noun: limbs
	nouns_percentage = float(nouns_count) / float(total_words)
	print("percent nouns = {0:.3f}% of all text".format(nouns_percentage*100))
	percentageDict['all_noun_in_all_words'] = nouns_percentage

	nouns_ratio= [pos.UPOSTAG for _, pos in csv_dict.iteritems()].count("NOUN")
	proper_to_ratio_percentage = float(proper_nouns_count) / float(nouns_ratio)
	print("proper nouns make up {0:.3f}% of all nouns".format((proper_to_ratio_percentage*100)))
	percentageDict['proper_noun_in_all_nouns'] = proper_to_ratio_percentage

	all_nouns_to_ratio_percentage = float(nouns_count) / float(nouns_ratio)
	print("regular nouns make up {0:.3f}% of all nouns".format((all_nouns_to_ratio_percentage*100)))
	percentageDict['regular_nouns_in_all_nouns'] = all_nouns_to_ratio_percentage

	#print(set([pos.XPOSTAG for _, pos in csv_dict.iteritems()])) # unquie tags
	#noun_tags = []
	#for row_num, pos in csv_dict.iteritems():
	#	if pos.UPOSTAG == "NOUN":
	#		noun_tags.append(pos.XPOSTAG)
	#print(set(noun_tags))
	
	print("Text is approximately {0} words".format(total_words))
	percentageDict['text_size'] = total_words
	return percentageDict  

def saveDatatoCSV(filename, percentDict):
	# save data from each run to a csv for graphing (if text is new or has been updated)
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "nounData_allText.csv"
	print("\n")

	fieldnames = ['FILENAME', 'TEXT_SIZE', 
				  'ALL_NOUNS_IN_ALL_WORDS', 'PRONOUNS_IN_ALL_WORDS',
				  'PROPER_NOUNS_IN_ALL_WORDS', 'REGULAR_NOUNS_IN_ALL_NOUNS',
				  'PROPER_NOUNS_IN_ALL_NOUNS']

	if not os.path.isfile("plot_percent_data/{0}".format(output_filename)): # if it doesn't exist, create csv file with dict data
		with open('plot_percent_data/{0}'.format(output_filename), 'w') as noun_data:
			writer = csv.DictWriter(noun_data, fieldnames=fieldnames)
			writer.writeheader() 
			writer.writerow({'FILENAME': os.path.basename(os.path.splitext(filename)[0]), 
							 'TEXT_SIZE': percentDict['text_size'],
							 'ALL_NOUNS_IN_ALL_WORDS': percentDict['all_noun_in_all_words'],
							 'PRONOUNS_IN_ALL_WORDS': percentDict['pronoun_in_all_words'],
							 'PROPER_NOUNS_IN_ALL_WORDS':  percentDict['proper_noun_in_all_words'],
							 'REGULAR_NOUNS_IN_ALL_NOUNS': percentDict['regular_nouns_in_all_nouns'],
							 'PROPER_NOUNS_IN_ALL_NOUNS': percentDict['proper_noun_in_all_nouns']
								})
		print("\n{0} created a new CSV NOUN DATA ".format(given_file.upper()))
	else: # csv file exists, copy data and re-generate 
		stored_results = [] # store old rows
		with open('plot_percent_data/{0}'.format(output_filename), 'r') as noun_data:
			reader = csv.DictReader(noun_data)
			for row in reader:
				stored_results.append(row) # store previous rows

		with open('plot_percent_data/{0}'.format(output_filename), 'w') as noun_data:
			new_file_to_append = os.path.basename(os.path.splitext(filename)[0])
			to_append = True
			writer = csv.DictWriter(noun_data, fieldnames=fieldnames)
			writer.writeheader() 
			for data_row in stored_results:
				if data_row['FILENAME'] == new_file_to_append:
					to_append = False # updated to an existing row rather than appended
					writer.writerow({'FILENAME':  new_file_to_append, 
									 'TEXT_SIZE': percentDict['text_size'],
									 'ALL_NOUNS_IN_ALL_WORDS': percentDict['all_noun_in_all_words'],
									 'PRONOUNS_IN_ALL_WORDS': percentDict['pronoun_in_all_words'],
									 'PROPER_NOUNS_IN_ALL_WORDS':  percentDict['proper_noun_in_all_words'],
									 'REGULAR_NOUNS_IN_ALL_NOUNS': percentDict['regular_nouns_in_all_nouns'],
									 'PROPER_NOUNS_IN_ALL_NOUNS': percentDict['proper_noun_in_all_nouns']
										})
					print("{0} updated in an existing CSV log".format(given_file.upper()))

				else:
					writer.writerow(data_row)
			if to_append: # if the file wasn't found, append to the end
				# add new data to the end (appended)
				writer.writerow({'FILENAME':  new_file_to_append, 
								 'TEXT_SIZE': percentDict['text_size'],
								 'ALL_NOUNS_IN_ALL_WORDS': percentDict['all_noun_in_all_words'],
								 'PRONOUNS_IN_ALL_WORDS': percentDict['pronoun_in_all_words'],
								 'PROPER_NOUNS_IN_ALL_WORDS':  percentDict['proper_noun_in_all_words'],
								 'REGULAR_NOUNS_IN_ALL_NOUNS': percentDict['regular_nouns_in_all_nouns'],
								 'PROPER_NOUNS_IN_ALL_NOUNS': percentDict['proper_noun_in_all_nouns']
									})
				print("{0} (new) appended to end of CSV NOUN DATA ".format(given_file.upper()))

	# save information as dictionary of dictionary values for graphing purposes {filename: {attributes:}}
	csv_data_results = {} # store old rows
	with open('plot_percent_data/{0}'.format(output_filename), 'r') as noun_data:
		reader = csv.DictReader(noun_data)
		for row in reader:
			csv_data_results[row['FILENAME']] = row # store previous rows
	return csv_data_results

def graphPOSdata(csv_data):
	# scatter plot of pronouns, nouns and word length (updated every run/edit)
	'''
	sample {'ALL_NOUNS_IN_ALL_WORDS': '0.17543859649122806',
	'FILENAME': 'sample', 'REGULAR_NOUNS_IN_ALL_NOUNS': '0.7407407407407407',
	'PROPER_NOUNS_IN_ALL_WORDS': '0.06140350877192982', 
	'PRONOUNS_IN_ALL_WORDS': '0.08771929824561403',
	'TEXT_SIZE': '114', 'PROPER_NOUNS_IN_ALL_NOUNS': '0.17543859649122806'}
	'''
	filenames = []
	text_size = []
	all_nouns_in_all_words = []
	pronouns_in_all_words = []
	regular_nouns_in_all_nouns = []
	proper_nouns_in_all_nouns = []
	for filename, subdict_attributes in csv_data.iteritems(): #store all rows in the same index of different lists
		filenames.append(filename)
		text_size.append(int(subdict_attributes['TEXT_SIZE']))
		all_nouns_in_all_words.append(float(subdict_attributes['ALL_NOUNS_IN_ALL_WORDS']))
		pronouns_in_all_words.append(float(subdict_attributes['PRONOUNS_IN_ALL_WORDS']))
		regular_nouns_in_all_nouns.append(float(subdict_attributes['REGULAR_NOUNS_IN_ALL_NOUNS']))
		proper_nouns_in_all_nouns.append(float(subdict_attributes['PROPER_NOUNS_IN_ALL_NOUNS']))

	(fig, ax) = plt.subplots(1, 1, figsize=(16, 16))
	ax.scatter(text_size, all_nouns_in_all_words)
	plt.title("POS DATA: Text size and All Nouns in All Words")
	for i, data in enumerate(filenames): # label all dots with text file name
		ax.annotate(data, (text_size[i], all_nouns_in_all_words[i]), fontsize=5)
	plt.ylabel("Percentage")
	ax.set_ylim([0.0, 1.0])
	ax.set_xlim(left=0)
	plt.xlabel("File Text Size (words)")
	plt.savefig('plot_percent_data/all_nouns_in_all_words.png')
	
	(fig, ax) = plt.subplots(1, 1, figsize=(16, 16))
	ax.scatter(text_size, pronouns_in_all_words)
	plt.title("POS DATA: Text size and Pronouns in All Words")
	for i, data in enumerate(filenames): # label all dots with text file name
		ax.annotate(data, (text_size[i], pronouns_in_all_words[i]), fontsize=5)
	plt.ylabel("Percentage")
	ax.set_ylim([0.0, 1.0])
	ax.set_xlim(left=0)
	plt.xlabel("File Text Size (words)")
	plt.savefig('plot_percent_data/pronouns_in_all_words.png')

	(fig, ax) = plt.subplots(1, 1, figsize=(16, 16))
	ax.scatter(text_size, regular_nouns_in_all_nouns)
	plt.title("POS DATA: Text size and Regular Nouns in All Nouns")
	for i, data in enumerate(filenames): # label all dots with text file name
		ax.annotate(data, (text_size[i], regular_nouns_in_all_nouns[i]), fontsize=5)
	plt.ylabel("Percentage")
	ax.set_ylim([0.0, 1.0])
	ax.set_xlim(left=0)
	plt.xlabel("File Text Size (words)")
	plt.savefig('plot_percent_data/regular_nouns_in_all_nouns.png')

	(fig, ax) = plt.subplots(1, 1, figsize=(16, 16))
	ax.scatter(text_size, proper_nouns_in_all_nouns)
	plt.title("POS DATA: Text size and Pronouns in All Nouns")
	for i, data in enumerate(filenames): # label all dots with text file name
		ax.annotate(data, (text_size[i], proper_nouns_in_all_nouns[i]), fontsize=5)
	plt.ylabel("Percentage")
	ax.set_ylim([0.0, 1.0])
	ax.set_xlim(left=0)
	plt.xlabel("File Text Size (words)")
	plt.savefig('plot_percent_data/proper_nouns_in_all_nouns.png')

	print("DATA PLOT POS UPDATED")

########################################################################
## Output pos into csv
def outputCSVconll(filename, dict_parts_speech, filednames):
	# save conll parser and pos to csv
	'''
	0 - ID (index in sentence), index starts at 1
	1 - FORM (exact word)
	2 - LEMMA (stem of word form)
	3 - UPOSTAG (universal pos tag)
	4 - XPOSTAG (Language-specific part-of-speech tag)
	5 - FEATS (List of morphological features)
	6 - HEAD (Head of the current token, which is either a value of ID or zero (0))
	7 - DEPREL (Universal Stanford dependency relation to the HEAD (root iff HEAD = 0))
	8 - DEPS (List of secondary dependencies)
	9 - MISC (other annotation)
	'''
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	output_filename = "pos_{0}.csv".format(given_file.upper())

	with open('csv_pos/{0}'.format(output_filename), 'w+') as pos_data:
		writer = csv.DictWriter(pos_data, fieldnames=fieldnames)
		writer.writeheader() 
		for i in range(len(dict_parts_speech)):
			sentence_pos_lst = dict_parts_speech[i][1]
			for pos in sentence_pos_lst:
				writer.writerow({'SENTENCE_INDEX': i, 
								'FORM': pos[1],
								'XPOSTAG': pos[4],
								'UPOSTAG': pos[3],
								'ID': pos[0],
								'SENTENCE_LENGTH': len(dict_parts_speech[i][0].split()),
								'LEMMA': pos[2],
								'FEATS': pos[5],
								'HEAD': pos[6],
								'DEPREL': pos[7],
								'DEPS':pos[8],
								'MISC': pos[9],
								'SENTENCE': dict_parts_speech[i][0],
								'IS_DIALOUGE': isDialogue(dict_parts_speech[i][0])
								})

	print("\nCSV POS output saved as {0}".format(output_filename))

########################################################################
## Parse Arguments, running main

if __name__ == '__main__':
	start_time = datetime.now()
	import argparse
	parser = argparse.ArgumentParser(description="flag format given as: -F <filename>")
	parser.add_argument('-F', '-filename', help="filename from Raw_Text directory")
	args = parser.parse_args()

	filename = args.F

	if filename is None:
		print("\n\tWARNING: File not given to tokenize, exiting...\n")
		exit()

	tokens_in_order = readFile(filename)
	tokens_as_string = " ".join(tokens_in_order)
	tokens_as_string = tokens_as_string.translate(None, "\r")

	token_sentence_dict = tokenizeSentence(tokens_as_string)
	#for key, value in token_sentence_dict.iteritems():
	#	print("k={0} is quote = {1}".format(value, isDialogue(token_sentence_dict[key])))

	# check to see if file has already been saved in csv, otherwise run script
	given_file = os.path.basename(os.path.splitext(filename)[0]) # return only the filename and not the extension
	print("RUNNING: {0}".format(given_file.upper()))
	output_filename = "pos_{0}.csv".format(given_file.upper())
	#print(output_filename)
	csv_local_dir = "{0}/csv_pos/{1}".format(os.getcwd(), output_filename)

	fieldnames = ['SENTENCE_INDEX',
				'FORM',
				'XPOSTAG',
				'UPOSTAG',
				'ID',
				'SENTENCE_LENGTH',
				'LEMMA',
				'FEATS',
				'HEAD',
				'DEPREL',
				'DEPS',
				'MISC',
				'SENTENCE',
				'IS_DIALOUGE'
				]

	# if file has been modified more recently than the associated csv
	file_has_been_modified_recently = False
	if os.path.isfile(csv_local_dir): # if file exists, then check if modified
		file_has_been_modified_recently = os.path.getmtime("{0}/{1}".format(os.getcwd(), filename)) > os.path.getmtime(csv_local_dir)
		#print("file has been modifed = {0}".format(file_has_been_modified_recently))
	# if file does not exist in the csv folder
	if not os.path.isfile(csv_local_dir) or file_has_been_modified_recently: 
		#print("pos needs to be calculated...")
		dict_parts_speech = partsOfSpeech(token_sentence_dict)
		outputCSVconll(filename, dict_parts_speech, fieldnames)

	# create named tuple from csv row
	PosCSV = namedtuple('PosCSV', fieldnames)
	pos_dict = {}
	total_words = 0
	with open(csv_local_dir, "rb") as csv_file:
		csvreader = csv.reader(csv_file)
		next(csvreader) # skip header
		id_count = 0
		for line in csvreader:
			pos_named_tuple = PosCSV._make(line)
			pos_dict[id_count] = pos_named_tuple
			id_count += 1
			if pos_named_tuple.MISC != 'punct' and pos_named_tuple.XPOSTAG != 'POS': # if row isn't puntuation or 's
				total_words += 1
	# index proper nouns
	grouped_named_ent_lst = findProperNamedEntity(pos_dict) # return a list of tuples with elements in order for nnp
	#print("Characters in the text (set): {0}\n".format(list(set(x for l in grouped_named_ent_lst.values() for x in l))))
	character_entities_group = groupSimilarEntities(grouped_named_ent_lst)
	#print("Characters in the text (ent): {0}\n".format(character_entities_group))
	sub_dictionary_one_shot_lookup = lookupSubDictionary(character_entities_group)
	#print("dictionary for one degree of nouns: {0}".format(sub_dictionary_one_shot_lookup))

	global_ent_dict = mostCommonGNE(sub_dictionary_one_shot_lookup)

	# index pronouns
	pronoun_index_dict = findPronouns(pos_dict)
	#print("\n\npronoun index dictionary: {0}".format(pronoun_index_dict))

	# print/display graphs with pos data
	percent_ratio_dict = percentagePos(total_words, pos_dict) # print percentage of nouns/pronouns
	csv_data = saveDatatoCSV(filename, percent_ratio_dict)
	#graphPOSdata(csv_data)
	
	# gne hierarchy of names
	gne_tree = gneHierarchy(character_entities_group[0])
	loaded_gender_model = loadDTModel() # load model once, then use to predict
	gender_gne = determineGenderName(loaded_gender_model, gne_tree)

	# SET UP FOR MANUAL TESTING (coreference labels calls csv to be tagged by hand for accuracy)
	manual_tag_dir = "manual_tagging/manualTagging_{0}.csv".format(os.path.basename(os.path.splitext(filename)[0]).upper())
	if not os.path.isfile(manual_tag_dir) or file_has_been_modified_recently: # checks csv again to see if it has been updated
		coreferenceLabels(filename, pos_dict, sub_dictionary_one_shot_lookup, global_ent_dict, pronoun_index_dict)

	#for key, value in gne_tree.iteritems():
	#	print("\ngne base name: {0} is {1}\n{2}".format(key, gender_gne[key], value))

	coreferenceResolution(manual_tag_dir, gender_gne, loaded_gender_model)
	
	#identifyMainCharacter(manual_tag_dir)

	# GENERATE NETWORKX
	# generate a tree for gne names
	# {Dr Urbino: {'Dr': ['Dr', 'Dr Juvenal Urbino', 'Dr Urbino'], 'Urbino': ['Urbino']} }
	#generateGNEtree(gne_tree, filename)
	# generate network graphs
	#networkGraphs(gne_tree)

	print("\nPre-processing ran for {0}".format(datetime.now() - start_time))

########################################################################
## TODO: 
	# TODO: Predict name of first-person character
	# TODO: find possesive 'you've' and 'my'
	# TODO: check CAPTALIZED WORDS as their lower case counterparts before saving

	# TODO: clean up returned names based on Counter frequency (names should appear more than once)
	# TODO: set up progress bar for proper noun and pronoun splicing for large text
	
	#TODO Next: import local file to predict male/female (he/she) with a given list of names
	#x number of sentences around to find proper noun
