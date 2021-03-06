import os
import sys
import re
import time
import argparse
import math

class DocClusterMap:

	def __init__(self,file):

		file_read = file.readlines()
		file.close()

		self.doc_cluster_map = []
		self.cluster_sizes = {}
		self.cluster_sizes['total'] = 0

		for index in xrange(len(file_read)):
			line_splitted = file_read[index].split(" ")
			self.doc_cluster_map.append(int(line_splitted[1]))

			try:
				self.cluster_sizes[int(line_splitted[1])] += 1
			except KeyError:
				self.cluster_sizes[int(line_splitted[1])] = 1

			self.cluster_sizes['total'] += 1

	def get_cluster_id(self,document_id):

		return self.doc_cluster_map[document_id-1]

	def get_cluster_size(self,cluster_id):

		return self.cluster_sizes[cluster_id]

class QueryResults:
	
	def __init__(self,file):

		file_read = file.read()
		file.close()

		file_parsed = re.findall("([0-9]*)?\t.*?\t([0-9]*)?\t[0-9]*\t([0-9]*.[0-9]*)?\t.*?",file_read)

		self.query_results = []

		latest_query_id = 0
		for parsed_line in file_parsed:

			query_id = int(parsed_line[0])
			if query_id != latest_query_id:
				while(latest_query_id < query_id):
					self.query_results.append([])
					latest_query_id += 1

			self.query_results[query_id-1].append((int(parsed_line[1]),float(parsed_line[2])))

	def get_results(self,query_id,result_size):
		
		return self.query_results[query_id-1][0:result_size]

	def get_query_count(self):

		return len(self.query_results)

class ResourceSelectionRedde:

	def __init__(self,query_results,doc_cluster_map):

		cluster_score_dict = {}
		for (doc_id,doc_score) in query_results:
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			try:
				cluster_score_dict[cluster_id] += 1
			except KeyError:
				cluster_score_dict[cluster_id] = 1

		self.sorted_clusters = sorted(cluster_score_dict.items(),key = lambda x:x[1])
		self.sorted_clusters.reverse()

	def get_top_k_clusters(self,k):

		return [x[0] for x in self.sorted_clusters[0:k]]

class ResourceSelectionReddeTop:

	def __init__(self,query_results,doc_cluster_map):

		cluster_score_dict = {}
		for (doc_id,doc_score) in query_results:
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			try:
				cluster_score_dict[cluster_id] += doc_score
			except KeyError:
				cluster_score_dict[cluster_id] = doc_score

		self.sorted_clusters = sorted(cluster_score_dict.items(),key = lambda x:x[1])
		self.sorted_clusters.reverse()

	def get_top_k_clusters(self,k):

		return [x[0] for x in self.sorted_clusters[0:k]]

class ResourceSelectionCRCSExp:

	def __init__(self,query_results,doc_cluster_map,alpha,beta):

		cluster_score_dict = {}
		for index,(doc_id,doc_score) in enumerate(query_results):
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			try:
				cluster_score_dict[cluster_id] += alpha * math.exp(-1 * beta * (index + 1))
			except KeyError:
				cluster_score_dict[cluster_id] = alpha * math.exp(-1 * beta * (index + 1))

		self.sorted_clusters = sorted(cluster_score_dict.items(),key = lambda x:x[1])
		self.sorted_clusters.reverse()

	def get_top_k_clusters(self,k):

		return [x[0] for x in self.sorted_clusters[0:k]]

class ResourceSelectionCRCSLin:

	def __init__(self,query_results,doc_cluster_map):

		cluster_score_dict = {}
		for index,(doc_id,doc_score) in enumerate(query_results):
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			try:
				cluster_score_dict[cluster_id] += len(query_results) - (index + 1)
			except KeyError:
				cluster_score_dict[cluster_id] = len(query_results) - (index + 1)

		self.sorted_clusters = sorted(cluster_score_dict.items(),key = lambda x:x[1])
		self.sorted_clusters.reverse()

	def get_top_k_clusters(self,k):

		return [x[0] for x in self.sorted_clusters[0:k]]

class ResourceSelectionGAVG:

	def __init__(self,query_results,doc_cluster_map,doc_per_cluster):

		cluster_doc_dict = {}
		for (doc_id,doc_score) in query_results:
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			try:
				cluster_doc_dict[cluster_id].append(doc_score)
			except KeyError:
				cluster_doc_dict[cluster_id] = [doc_score]

		cluster_score_dict = {}
		for cluster_id,score_array in cluster_doc_dict.iteritems():
			min_score = query_results[-1][1]
			
			while len(score_array) < doc_per_cluster:
				score_array.append(min_score)
			cluster_score = 1
			for doc_score in score_array[0:doc_per_cluster]:
				cluster_score *= doc_score
			cluster_score_dict[cluster_id] = cluster_score

		self.sorted_clusters = []

		self.sorted_clusters = sorted(cluster_score_dict.items(),key = lambda x:x[1])
		self.sorted_clusters.reverse()

	def get_top_k_clusters(self,k):

		return [x[0] for x in self.sorted_clusters[0:k]]

class ResultProducer:

	def __init__(self,query_id,cluster_list,query_results,result_size):

		self.query_id = query_id
		self.cluster_list = cluster_list
		self.query_results = query_results
		self.result_size = result_size

	def produce_output(self,output_file):

		result_index = 1
		for (doc_id,doc_score) in self.query_results:
			cluster_id = doc_cluster_map.get_cluster_id(doc_id)
			if cluster_id in self.cluster_list:
				doc_score = "%.6f" % doc_score
				# print "{}\tQ0\t{}\t{}\t{}\tfs".format(self.query_id,doc_id,result_index,doc_score)
				output_file.write("{}\tQ0\t{}\t{}\t{}\tfs\n".format(self.query_id,doc_id,result_index,doc_score))
				result_index += 1
				if result_index > self.result_size:
					break

		no_of_documents_in_selected_clusters = 0
		for cluster_id in self.cluster_list:
			no_of_documents_in_selected_clusters += doc_cluster_map.get_cluster_size(cluster_id)
		return (100.0*no_of_documents_in_selected_clusters)/doc_cluster_map.get_cluster_size('total')



parser = argparse.ArgumentParser(description='Resource Selection Algorithms')
parser.add_argument('result_1', type=argparse.FileType('r'), help='result file of queries on main index')
parser.add_argument('result_2', type=argparse.FileType('r'), help='result file of queries on CSI')
parser.add_argument('cluster_concat_file', type=argparse.FileType('r'), help='file of document_id cluster_id pairs')
parser.add_argument('-method', action="store",help='resource selection method (default: Redde)',default='Redde',choices=['Redde', 'Redde.top', 'CRCSExp', 'CRCSLin', 'GAVG'])
parser.add_argument('-no_of_resource', type=int, action="store", help='no of resource to select (default: 10)', default=10, choices=[1,3,5,10,20,30,40,50,60,70,80,90,100])
parser.add_argument('-no_of_CSI_result', type=int, action="store", help='no of CSI result for resource selection (default:100)', default=100, choices=[50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000])
parser.add_argument('-result_size', type=int, action="store", help='no of result page desired (default: 20)', default=20, choices=[10,20,30,40,50,60,70,80,90,100])
parser.add_argument('-crcs_alpha', type=float, action="store", help='alpha component of CRCS Exp Formula (default:1.2)',default=1.2)
parser.add_argument('-crcs_beta', type=float, action="store", help='beta component of CRCS Exp Formula (default:2.8)',default=2.8)
parser.add_argument('-gavg_k', type=int, action="store", help='k component of GAVG (default:5)',default=5)
ARGUMENTS = parser.parse_args()


doc_cluster_map = DocClusterMap(ARGUMENTS.cluster_concat_file)

query_results_on_original_index	= QueryResults(ARGUMENTS.result_1)
query_results_on_CSI			= QueryResults(ARGUMENTS.result_2)

if query_results_on_original_index.get_query_count() != query_results_on_CSI.get_query_count():
	print "Query Counts Does Not Match!"

percentage_of_documents_in_selected_clusters_total = 0
filename = ARGUMENTS.result_2.name + "_" + ARGUMENTS.method
output_file = open(filename,"w")
for query_index in range(query_results_on_original_index.get_query_count()):
	
	top_k_results_on_CSI = query_results_on_CSI.get_results(query_index+1,ARGUMENTS.no_of_CSI_result)

	if ARGUMENTS.method == 'Redde':
		resource_selection_mode = ResourceSelectionRedde(top_k_results_on_CSI,doc_cluster_map)
	elif ARGUMENTS.method == 'Redde.top':
		resource_selection_mode = ResourceSelectionReddeTop(top_k_results_on_CSI,doc_cluster_map)
	elif ARGUMENTS.method == 'CRCSExp':
		resource_selection_mode = ResourceSelectionCRCSExp(top_k_results_on_CSI,doc_cluster_map,ARGUMENTS.crcs_alpha,ARGUMENTS.crcs_beta)
	elif ARGUMENTS.method == 'CRCSLin':
		resource_selection_mode = ResourceSelectionCRCSLin(top_k_results_on_CSI,doc_cluster_map)
	elif ARGUMENTS.method == 'GAVG':
		resource_selection_mode = ResourceSelectionGAVG(top_k_results_on_CSI,doc_cluster_map,ARGUMENTS.gavg_k)
	else:
		print 'Requested resource selection method is not available'
			
	# cluster_list = resource_selection_mode.get_top_k_clusters(ARGUMENTS.no_of_resource)
	cluster_list = resource_selection_mode.get_top_k_clusters(ARGUMENTS.no_of_resource)
	# cluster_list = range(100)
	# print cluster_list
	# break
	query_results = query_results_on_original_index.get_results(query_index+1,-1)
	
	result_producer =  ResultProducer(query_index+1,cluster_list,query_results,ARGUMENTS.result_size)
	percentage_of_documents_in_selected_clusters = result_producer.produce_output(output_file)
	percentage_of_documents_in_selected_clusters_total += percentage_of_documents_in_selected_clusters
output_file.close()
print percentage_of_documents_in_selected_clusters_total / query_results_on_original_index.get_query_count()
