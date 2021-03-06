#ifndef _CONSTANTS_H_
#define _CONSTANTS_H_

typedef enum {
    SUCCESS,
    EMPTY_CONFIG_DATA,
    COULD_NOT_ALLOCATE_TERMS,
    COULD_NOT_ALLOCATE_DOCUMENTS,
    COULD_NOT_OPEN_WORDLIST,
    COULD_NOT_OPEN_DOCUMENT_INFO,
    NULL_DOCUMENT,
    COULD_NOT_ALLOCATE_TERM_VECTORS,
    COULD_NOT_OPEN_DOCUMENT_VECTORS_FILE,
    COULD_NOT_READ_TERM_VECTORS_PROPERLY,
    COULD_NOT_ALLOCATE_CLUSTERS,
    COULD_NOT_ALLOCATE_DOCUMENT_IDS,
    COULD_NOT_OPEN_CLUSTER_DOCUMENT_IDS_FILE,
    COULD_NOT_WRITE_DOCUMENT_ID,
    COULD_NOT_ALLOCATE_TERMS_COC_COUNTS,
    COULD_NOT_OPEN_INVERTED_INDEX,
    COULD_NOT_OPEN_DOC_TO_CLUSTER_MAP_FOR_C1,
    COULD_NOT_OPEN_DOC_TO_CLUSTER_MAP_FOR_C2,
    COULD_NOT_ALLOCATE_DOC_TO_CLUSTER_MAP,
    COULD_NOT_READ_DOC_TO_CLUSTER_MAP,
    WARNING_AT_CLUSTER_OCCURENCE_COMPARE,
    COULD_NOT_OPEN_COC_RESULT_FILE
} State;

extern char* const state_messages[];
extern char* const document_vectors_file_names[];

#endif /* not defined _CONSTANTS_H_ */
