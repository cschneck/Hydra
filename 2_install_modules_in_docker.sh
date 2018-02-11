#!/bin/bash
echo "install modules needed to run inside docker container..."
echo ""
sed -i -e 's/archive.ubuntu.com\|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
apt-get update

echo ""
echo "install local modules"
echo 'y' | apt-get install vim
pip install progressbar
echo 'y' | apt-get install python-pandas

echo ""
echo "install nltk for tokens"
pip install nltk
echo -e "import nltk\nnltk.download('punkt')\nnltk.download('averaged_perceptron_tagger')" | python

echo "copying tagger for POS, replaced demo.sh"
cp /root/models/syntaxnet/Ishmael/pos_tagger.sh ~/models/syntaxnet/syntaxnet/

echo "remove logging verbosity for tensorflow"
DIR=/root/models/syntaxnet/syntaxnet
LogVerbose="parser_eval.py parser_trainer.py conll2tree.py"

for file_i in $LogVerbose; do
   #sed -i "/logging.set_verbosity/ s/^#*/#/" "${DIR}/${file_i}";
   sed -i "/logging.set_verbosity*/d" "${DIR}/${file_i}";
done

LOGCC="arc_standard_transitions_test.cc embedding_feature_extractor.cc lexicon_builder.cc reader_ops.cc shared_store_test.cc tagger_transitions_test.cc term_frequency_map.cc"

for file_j in $LOGCC; do
   chmod +x "${DIR}/${file_j}";
   sed -i "/LOG(INFO)*/d" "${DIR}/${file_j}";
done