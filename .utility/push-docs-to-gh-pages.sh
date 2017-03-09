#!/bin/bash

cd docs
pip3 install -r requirements.txt

echo -e "Generating static HTML pages for documentation...\n"

make html

echo -e "Publishing documentation...\n"

cp -Rf _build/html $HOME/docs

cd $HOME
git config --global user.email "travis@travis-ci.org"
git config --global user.name "travis-ci"
git clone --quiet --branch=gh-pages https://${GH_TOKEN}@github.com/pri22296/progressindicator gh-pages > /dev/null

cd gh-pages
git rm -rf ./*
cp -Rf $HOME/docs/* .
touch .nojekyll
git add -f .
git commit -m "Latest docs on successful travis build $TRAVIS_BUILD_NUMBER auto-pushed to gh-pages"
git push -fq origin gh-pages > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "Published docs to gh-pages.\n"
    exit 0
else
    echo -e "Publishing failed. Maybe the access-token was invalid or had insufficient permissions.\n"
    exit 1
fi
