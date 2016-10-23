set -xe

cd ../../test

git checkout -b generate_test_patch
sed -i'' -e '91,97d' test_basic.py
rm test_feedback.py
git diff > ../conda/python-autowig/windows.patch
git add test_feedback.py test_basic.py
git commit -m 'patch generated'
git checkout master
git branch -D generate_test_patch

git checkout -b generate_test_patch
rm test_feedback.py
git diff > ../conda/python-autowig/macosx.patch
rm test_subset.py
git diff > ../conda/python-autowig/travis-ci.patch
git add test_feedback.py test_subset.py
git commit -m 'patch generated'
git checkout master
git branch -D generate_test_patch