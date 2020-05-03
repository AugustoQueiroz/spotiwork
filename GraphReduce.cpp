#include <iostream>
#include <fstream>
#include <set>
#include <map>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

map<string, int> getNodeLabels(string inputFilePath) {
	ifstream inputFile(inputFilePath);

	map<string, int> nodeMap;

	string node;
	int i = 0;
	while (inputFile >> node) {
		if (nodeMap[node] == 0) {
			nodeMap[node] = i;
			i++;
		}
	}

	return nodeMap;
}

vector<vector<int>> getEdges(string inputFilePath, map<string, int> nodeMap) {
	ifstream inputFile(inputFilePath);

	vector<vector<int>> edges = vector<vector<int>>(nodeMap.size());

	string node1, node2;
	while (inputFile >> node1 >> node2) {
		edges[nodeMap[node1]].push_back(nodeMap[node2]);
	}

	return edges;
}

void saveGraph(map<string, int> nodeMap, vector<vector<int>> edges, string outputFilePath) {
	vector<string> nodeLabels = vector<string>(edges.size());

	for (auto it = nodeMap.begin(); it != nodeMap.end(); it++) {
		nodeLabels[it->second] = it->first;
	}

	ofstream outputFile(outputFilePath, ofstream::binary);

	for (auto it = nodeLabels.begin(); it != nodeLabels.end(); it++) {
		outputFile << *it << "\t";
		//outputFile.write(it->c_str(), it->size()*sizeof(char));
	}

	outputFile << endl;

	for (auto it = edges.begin(); it != edges.end(); it++) {
		for (auto it2 = it->begin(); it2 != it->end(); it2++) {
			outputFile.write((char*) &(*it2), sizeof(int));
			//outputFile << *it2 << " ";
		}
		outputFile << endl;
	}
}

int main() {
	string inputFilePath = "artists.net";

	map<string, int> nodeMap = getNodeLabels(inputFilePath);
	vector<vector<int>> edges = getEdges(inputFilePath, nodeMap);

	saveGraph(nodeMap, edges, "artists_reduced.net");
}
