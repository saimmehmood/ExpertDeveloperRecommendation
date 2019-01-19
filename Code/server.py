import os, requests, json
from bottle import get, post, route, error, request, run, static_file
from pprint import pprint
from datetime import datetime


# projectRoot = "~/Projects/MSED/" if os.path.isdir("~/Projects/MSED") else "../" 
#projectRoot = "/home/tipech/Projects/MSED/"
results_count = 100
commit_frequency = 1.0  # 1 commit per month

# ================= Static Pages ================
@route('/')
def static_html():
	return static_file("index.html", root = projectRoot )


@post('/search')
def search_function():

	query_must = []
	query_should = []

	# Turning fields into queries
	developer = request.forms.get("developer")
	if( developer ):
		query_must.append( {"match":{"developer": developer}} )
	
	if( request.forms.get("total_duration") == "on" ):
		total_duration_1 = int(request.forms.get("total_duration_1"))
		total_duration_2 = int(request.forms.get("total_duration_2"))
		query_must.append( {"range":{"total_duration": {
				"gte": total_duration_1*30*24*60*60,
				"lte": total_duration_2*30*24*60*60,
				"boost": 2.0
			}}} )

	repo = request.forms.get("repo")
	if( repo ):
		query_must.append( {"match":{"repos": repo}} )

	if( request.forms.get("active") == "on" ):
		query_must.append( {"range":{"last_commit": {
				"gte": (int(datetime.now().timestamp()) - 6*30*24*60*60),
				"boost": 2.0
			}}} )


	# ============== skill 1 ====================

	skill_1 = request.forms.get("language_1") 
	if( skill_1 != "" ):

		skill_1_duration_1 = int(request.forms.get("language_1_duration_1"))
		skill_1_duration_2 = int(request.forms.get("language_1_duration_2"))
		if(skill_1_duration_2 < skill_1_duration_1):
			tmp = skill_1_duration_2
			skill_1_duration_2 = skill_1_duration_1
			skill_1_duration_1 = tmp

		nested_must = []
		nested_must.append( {"match" : {"languages.name": {"query": skill_1, "boost": 4.0 }}} )

		if(request.forms.get("language_1_duration") == "on"):
			nested_must.append( {"range":{"languages.duration": { 
					"gte": skill_1_duration_1*30*24*60*60,
					"lte": skill_1_duration_2*30*24*60*60,
					"boost": 2.0
				}}} )

			if(request.forms.get("language_1_frequency") == "on"):

				nested_must.append( {"range":{"languages.commit_count": { 
						"gte": skill_1_duration_1 * commit_frequency,
						"boost": 2.0
					}}} )			

		query_must.append( {"nested": { "path": "languages", "query": {"bool": {"must": nested_must }}}})


	# ============== skill 2 ====================

	skill_2 = request.forms.get("language_2") 
	if( skill_2 != "" ):

		skill_2_duration_1 = int(request.forms.get("language_2_duration_1"))
		skill_2_duration_2 = int(request.forms.get("language_2_duration_2"))
		if(skill_2_duration_2 < skill_2_duration_1):
			tmp = skill_2_duration_2
			skill_2_duration_2 = skill_2_duration_1
			skill_2_duration_1 = tmp

		nested_must = []
		nested_must.append( {"match" : {"languages.name": {"query": skill_2, "boost": 4.0 }}} )

		if(request.forms.get("language_2_duration") == "on"):
			nested_must.append( {"range":{"languages.duration": { 
					"gte": skill_2_duration_1*30*24*60*60,
					"lte": skill_2_duration_2*30*24*60*60,
					"boost": 2.0
				}}} )

			if(request.forms.get("language_2_frequency") == "on"):

				nested_must.append( {"range":{"languages.commit_count": { 
						"gte": skill_2_duration_1 * commit_frequency,
						"boost": 2.0
					}}} )			

		query_must.append( {"nested": { "path": "languages", "query": {"bool": {"must": nested_must }}}})


	# ============== skill 3 ====================

	skill_3 = request.forms.get("language_3") 
	if( skill_3 != "" ):

		skill_3_duration_1 = int(request.forms.get("language_3_duration_1"))
		skill_3_duration_2 = int(request.forms.get("language_3_duration_2"))
		if(skill_3_duration_2 < skill_3_duration_1):
			tmp = skill_3_duration_2
			skill_3_duration_2 = skill_3_duration_1
			skill_3_duration_1 = tmp

		nested_must = []
		nested_must.append( {"match" : {"languages.name": {"query": skill_3, "boost": 4.0 }}} )

		if(request.forms.get("language_3_duration") == "on"):
			nested_must.append( {"range":{"languages.duration": { 
					"gte": skill_3_duration_1*30*24*60*60,
					"lte": skill_3_duration_2*30*24*60*60,
					"boost": 2.0
				}}} )

			if(request.forms.get("language_3_frequency") == "on"):

				nested_must.append( {"range":{"languages.commit_count": { 
						"gte": skill_3_duration_1 * commit_frequency,
						"boost": 2.0
					}}} )			

		query_must.append( {"nested": { "path": "languages", "query": {"bool": {"must": nested_must }}}})




	query = {"query": {"bool": {} } }
	if(query_must):
		query['query']['bool']['must'] = query_must
	if(query_should):
		query['query']['bool']['should'] = query_should

	# pprint(query)
	json_str = json.dumps(query).replace('\"', '\"')
	response = requests.get('http://130.63.97.168:9200/_search?pretty',
		auth=('elastic','elastic'),
		headers={'Content-Type': 'application/json'},
		data=json_str,
		params={'size':results_count})
	results = json.loads(response.text)
	# pprint(results)


	results_html = ""

	false_hits = 0

	for hit in results['hits']['hits']:
		if('developer' not in hit['_source']):
			false_hits = 1

	if(false_hits):
		results_html += "Invalid query.<br>"
	else:
		results_html += "Total hits: " + str(results['hits']['total']) + "<br>"

		for hit in results['hits']['hits']:

			if('developer' in hit['_source']):

				results_html += "<li><h3>" + hit['_source']['developer'] + "</h3>"
				results_html += "<p>Email: &nbsp;&nbsp;" + hit['_source']['email'] + "</p>"
				results_html += "<p>Contributor since: &nbsp;&nbsp;" + datetime.fromtimestamp( float(hit['_source']['first_commit']) ).strftime('%B %d, %Y') + "<br>"
				results_html += "Last contribution: &nbsp;&nbsp;" + datetime.fromtimestamp( float(hit['_source']['last_commit']) ).strftime('%B %d, %Y')

				if (int(hit['_source']['last_commit']) > int(datetime.now().timestamp()) - 6*30*24*60*60):
					results_html += " (currently active)<br>"
					results_html += "Contributor for: &nbsp;&nbsp;" + seconds_to_string(datetime.now().timestamp() - int(hit['_source']['first_commit'])) + "</p>"
				else:
					results_html += " (not currently active)<br>"
					results_html += "Contributor for: &nbsp;&nbsp;" + seconds_to_string(hit['_source']['total_duration']) + "</p>"


				results_html += " <ul><h4>Skills:</h4>"

				last_skill = ""
				
				for skill in hit['_source']['languages']:

					if(skill['name'] != last_skill):

						results_html += " <li><p><b>" + skill['name'] + "</b></p>"
						results_html += "<p>Known since: &nbsp;&nbsp;" + datetime.fromtimestamp( float(skill['first_language_commit']) ).strftime('%B %d, %Y') + "<br>"
						results_html += "Worked for: &nbsp;&nbsp;" + seconds_to_string(skill['duration']) + "<br>"
						results_html += "Contributed: &nbsp;&nbsp;" + str(skill['commit_count']) + " commits, altering &nbsp;" + str(skill['files']) + " files in total</p></li>"
						last_skill = skill['name']

				results_html += " </ul>"


				results_html += " <ul><h4>Repositories:</h4>"

				for repo in hit['_source']['repos']:

					results_html += " <li>" + repo + "</li>"

				results_html += " </ul>"
				results_html += " <p>Relevance score: " + str(hit['_score']) + "</p>"
				results_html += " </li><hr>"



	response = ('<!DOCTYPE html><html><head><title>Expert Developer Search Results</title></head><body><h2>Search Results:</h2><ul><hr>'
		+ results_html
		+ '</ul><a href="/">Back to Search</a></body></html>')

	return response






# =============== Help Functions ================
def seconds_to_string(seconds):

	days = int(int(seconds) / (24*60*60))
	result = ""
	
	if (days > 356):
		result += str(int(days/356)) + " years, "
	if (days > 30):
		result += str(int(days/30) % 12) + " months, "
	result += str((days % 30) + 1) + " days"

	return result



# ===================== Run =====================
run(host='0.0.0.0', port=8080, debug=True, reloader=True)