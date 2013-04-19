#!/usr/bin/python 

## this program normalizes all folders first, evaluates the systems and note the errors, finally show the suggestions, sorted by number of systems suggested it

## usage: python suggest_new_timeml_annotation.py gold_anntoation system_annotation1 system_annotation2 system_annotation3 system_annotationn

import os
import sys

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
	
		
suggest_new_timeml_anntoation()
