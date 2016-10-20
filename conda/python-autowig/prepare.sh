git checkout -b generate_test_patch
cd ../../test
sed -i'' -e '91,97d' test_basic.py
rm test_feedback.py
git diff > ../conda/python-autowig/test.patch
git add test_feedback.py test_basic.py
git commit -m 'patch generated'
git checkout master
git branch -D generate_test_patch