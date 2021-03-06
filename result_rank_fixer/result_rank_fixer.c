#include "../topic_based/c/Allocator.h"
#include <unistd.h>

void writeResults () {
    FILE *fp;
    int q_no, j, rank;
    char results_path[FILEPATH_LENGTH] = "";
    size_t len1 = strlen(config->results_path);
    memcpy(results_path, config->results_path, len1);
    memcpy(results_path+len1, "_fixed", 6);

    if (!(fp = fopen(results_path, "w"))) {
        return;
    }

    for (q_no = 0; q_no < config->number_of_query; q_no++) {
        rank = 1;
        for (j = 0; (j < config->number_of_preresults) && (rank <= config->number_of_results); j++) {
            if (results[q_no][j].doc_id != 0 && results[q_no][j].score != 0) {
                fprintf(fp, "%d\tQ0\t%d\t%d\t%lf\tfs\n", q_no + 1, results[q_no][j].doc_id, rank++, results[q_no][j].score);
            }
        }
    }

    fclose(fp);
    state = SUCCESS;
}

void loadResults () {
    FILE *fp;
    char temp[100];
    unsigned int query_id;
    unsigned int document_id;
    unsigned int rank;
    double score;

    if (!(fp = fopen(config->results_path, "r"))) {
        return;
    }

    while (!feof(fp)) {
        fscanf (fp, "%u %s %u %u %lf %s\n", &(query_id), temp, &(document_id),
                                           &(rank), &(score), temp);
        results[query_id-1][rank-1].doc_id = document_id;
        results[query_id-1][rank-1].score = score;
    }

    fclose(fp);
    state = SUCCESS;
}

int initFixer (Conf *conf) {
    if (!conf) {
        state = EMPTY_CONFIG_DATA;
        return -1;
    }

    config = conf;

    int i, j;
    long results_pointer_alloc_size = config->number_of_query * sizeof(Result *);
    long results_alloc_size = config->number_of_preresults * sizeof(Result);

    if (!(results = malloc(results_pointer_alloc_size))) {
        return -1;
    }

    for (int i = 0; i < config->number_of_query; i++) {
        if (!(results[i] = malloc(results_alloc_size))) {
            return -1;
        }
    }

    for (i = 0; i < config->number_of_query; i++) {
        for (j = 0; j < config->number_of_preresults; j++) {
            results[i][j].doc_id = 0;
            results[i][j].score = 0;
        }
    }

    state = SUCCESS;
    return 0;
}

int main (int argc, char *argv[]) {
    unsigned int number_of_preresults = 500;
    unsigned int number_of_results = 200;
    unsigned int number_of_query = 50;
    char results_path[FILEPATH_LENGTH] = "/home/eckucukoglu/Dropbox/arcelik/arcelikTeam/results_nospam/c500ns";

    Conf conf = {
        .number_of_preresults = number_of_preresults,
        .number_of_results = number_of_results,
        .number_of_query = number_of_query,
        .results_path = results_path
    };
    
    initFixer(&conf);
    loadResults();
    writeResults();

    return 0;
}
