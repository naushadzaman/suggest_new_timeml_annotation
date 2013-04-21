#!/usr/bin/python 

## this program normalizes all folders first, evaluates the systems and note the errors, finally show the suggestions, sorted by number of systems suggested it

## usage: python suggest_new_timeml_annotation.py gold_anntoation system_annotation1 system_annotation2 system_annotation3 system_annotationn

import re 
import os
import sys
import operator

debug = 1 

experiment_dir = 'data/'

def get_folder_name(path): 
	return '-'.join(path.split('/')).strip('-') 

def mkdir_cp_files(source, destination):
	if source[len(source)-1]  != '/': 
		source += '/'
	if os.path.exists(destination): 
		command = 'rm ' + destination + '/*'
		os.system(command)
	command = 'mkdir ' + destination 
	os.system(command)
	command = 'cp ' + source + '* ' + destination + '/'
	os.system(command)
	
	
def copy_folder(gold_annotation_folder, system_annotation): 

	all_folders = []
	gold_folder = experiment_dir + get_folder_name(gold_annotation_folder) 
	all_folders.append(gold_folder)
	mkdir_cp_files(gold_annotation_folder, gold_folder)
	system_folder = [] 
	for each in system_annotation: 
		if not (experiment_dir + get_folder_name(each)) in system_folder: 
			sys_dir = experiment_dir + get_folder_name(each)
			all_folders.append(sys_dir)
			system_folder.append(sys_dir)
			mkdir_cp_files(each, sys_dir)
		else: 
			print 'multiple folders found with ', get_folder_name(each)
			exit(0) 
	return all_folders 

def process_files(): 
	if len(sys.argv) < 3: 
		print 'usage: python suggest_new_timeml_annotation.py gold_anntoation system_annotation1 system_annotation2 system_annotation3 system_annotationn'
	gold_anntoation_folder = sys.argv[1]
	sys_annotation = [] 
	for i in range(2, len(sys.argv)): 
		sys_annotation.append(sys.argv[i])
	if debug >= 2: 
		print sys_annotation 

	all_folders = copy_folder(gold_anntoation_folder, sys_annotation)
	command = 'java -jar TimeML-Normalizer/TimeML-Normalizer.jar -a "'+ ';'.join(all_folders)+'"'
	if debug >= 2: 
		print command 
	os.system(command) 
	return all_folders 

def suggest_new_timeml_anntoation(): 
	debug_level = 0
	command = 'rm -rf ' + experiment_dir
	os.system(command)
	command = 'mkdir ' + experiment_dir 
	os.system(command)
	
	all_folders = process_files() 
	if debug >= 2: 
		print all_folders 
	for i in range(1, len(all_folders)):
		command = 'python TE3-evaluation.py ' + all_folders[0]+'-normalized/ ' + all_folders[i] +'-normalized/ ' + str(debug_level) + ' ' + experiment_dir
		print command 
		os.system(command)
	
def get_system_name(line):
	return re.sub('data-platinum-test-runs-', '', re.sub('-test-TaskABC-normalized', '', line))
	
def get_entity(line): 
	entity = re.findall('[te]id="[^"]*"', line)[0]
	entity = re.sub('[te]id=', '', entity)
	entity = re.sub('"', '', entity)
	system = line.split('\t')[2]
	system = get_system_name(system)
	e_text = re.findall('>[^<]*<', line)[0]
	e_text = re.sub('>', '', re.sub('<', '', e_text))
	return entity, system, e_text 
	
def get_relations(line): 
	words = line.split('\t')
	relation = words[5] + '\t' + words[1] + ' ' + words[2] + ' ' + words[3] 
	system = get_system_name(words[4])
	return relation, system 
	

def rank_suggestions(source_dir, dest_dir, filename):
	
	entity_file = open(dest_dir + 'entity-'+filename, 'w')
	tlink_file = open(dest_dir + 'tlink-'+filename, 'w')
	if debug >= 2: 
		print filename 
	text = open(source_dir + filename).read() 
	new_entity = {} 
	new_entity_count = {} 
	entity2text = {} 
	new_tlink = {} 
	new_tlink_count = {} 
	for line in text.split('\n'): 
		if re.search('event', line) or re.search('timex', line): 
			entity, system, e_text = get_entity(line)
			#print entity, system 
			
			if not entity in new_entity: 
				new_entity[entity] = [] 
				entity2text[entity] = [] 
				new_entity_count[entity] = 0 
			new_entity[entity].append(system)	
			new_entity_count[entity] += 1 
			if not e_text in entity2text[entity]: 
				entity2text[entity].append(e_text)
		elif re.search('tlink', line): 
			relation, system = get_relations(line)
			#print system, relation
			if not relation in new_tlink: 
				new_tlink[relation] = [] 
				new_tlink_count[relation] = 0 
			new_tlink[relation].append(system)
			new_tlink_count[relation] += 1 
	
	sorted_e = sorted(new_entity_count.iteritems(), key=operator.itemgetter(1), reverse=True)
	sorted_r = sorted(new_tlink_count.iteritems(), key=operator.itemgetter(1), reverse=True)

	entity_file.write('==== NEW ENTITY SUGGESTION ===\n')
	for i in range(0, len(sorted_e)): 
		str_foo = sorted_e[i][0] + '\t' + str(sorted_e[i][1]) + '\t' + ', '.join(entity2text[sorted_e[i][0]]) + '\t' + ', '.join(new_entity[sorted_e[i][0]]) 
		entity_file.write(str_foo + '\n')
	entity_file.write('\n\n') 

	tlink_file.write('==== NEW TLINK SUGGESTION ===\n')
	for i in range(0, len(sorted_r)): 
		str_foo = sorted_r[i][0] + '\t' + str(sorted_r[i][1]) + '\t' + ', '.join(new_tlink[sorted_r[i][0]])
		tlink_file.write(str_foo + '\n')
	tlink_file.write('\n') 
	
	entity_file.close()
	tlink_file.close()

	
	
def rank_all_suggestions(): 
	source_dir = experiment_dir + 'raw_suggest_dir/'
	dest_dir = experiment_dir + 'suggest_dir/'
	if not os.path.exists(dest_dir):
		command = 'mkdir ' + dest_dir
		os.system(command)
	files = os.listdir(source_dir)
	for file in files: 
		if re.search('DS_Store', file): 
			continue
		rank_suggestions(source_dir, dest_dir, file)
		

		
suggest_new_timeml_anntoation()
rank_all_suggestions() 