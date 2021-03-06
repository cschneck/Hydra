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
pip install textblob

echo ""
echo "installing networkx for visuals"
pip install networkx
echo 'y' | apt install python-pydot python-pydot-ng graphviz python-pygraphviz
echo 'y' | apt-get install graphviz
pip install pydot
echo 'y' | apt-get install python-dev graphviz libgraphviz-dev pkg-config
pip install pygraphviz
pip install graphviz
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/" --upgrade --force-reinstall


echo ""
echo "install scikit learn"
pip install -U scikit-learn==0.19.1
#using most recent version gives: USERWARNING: Trying to unpickle estimator DictVectorizer from version 0.19.1 when using version XXXX. This might lead to breaking code or invalid results. Use at your own risk.
#cython is using a deprecated Numpy API, so this warning can be ignored, scikit-learn will still be installed
#Reference:http://docs.cython.org/en/latest/src/reference/compilation.html#configuring-the-c-build

echo ""
echo "install nltk for tokens"
pip install nltk
echo -e "import nltk\nnltk.download('punkt')\nnltk.download('averaged_perceptron_tagger')" | python

echo "copying tagger for POS, replaced demo.sh"
cp /root/models/syntaxnet/Hydra/pos_tagger.sh ~/models/syntaxnet/syntaxnet/

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

echo ""
echo "done installing, ready to run"
