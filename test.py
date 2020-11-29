from scripts.vocabulary_creation import VocabularyBuilder



vb = VocabularyBuilder()
vb.build_bag_of_words(data_path='./data/tsv/*/*.tsv', fields=['plot'])