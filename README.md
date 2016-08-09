<h1 id="autowig-automatic-wrapper-and-interface-generator">AutoWIG: Automatic Wrapper and Interface Generator</h1>
<p>High-level programming languages, like <em>Python</em> and <em>R</em>, are popular among scientists. They tend to be concise and readable, leading to a rapid development cycle, but suffer from performance drawback compare to compiled language. However, these languages allow to interface <em>C</em>, <em>C++</em> and <em>Fortran</em> code. By this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries. While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming. In this paper, we introduce <strong>AutoWIG</strong>, a <em>Python</em> library that wraps automatically <em>C++</em> libraries into high-level languages. Our solution consists in parsing <em>C++</em> code using <strong>LLVM</strong>/<strong>CLang</strong> technology and generating the wrappers using the <strong>Mako</strong> templating engine. Our approach is automatic, extensible, and can scale from simple <em>C++</em> libraries to very complex ones, composed of thousands of classes or using modern meta-programming constructs. The usage and extension of <strong>AutoWIG</strong> is also illustrated on a set of statistical libraries.</p>
<blockquote>
<p><strong>Summary</strong></p>
<dl>
<dt>License</dt>
<dd><p>CeCILL-C license</p>
</dd>
<dt>Version</dt>
<dd><p>0.1.0</p>
</dd>
<dt>Status</dt>
<dd><p><a href="https://travis-ci.org/VirtualPlants/AutoWIG"><img src="https://travis-ci.org/VirtualPlants/AutoWIG.svg?branch=master" alt="Travis" /></a> <a href="https://coveralls.io/github/VirtualPlants/AutoWIG?branch=master"><img src="https://coveralls.io/repos/github/VirtualPlants/AutoWIG/badge.svg?branch=master" alt="Coveralls" /></a> <a href="https://landscape.io/github/VirtualPlants/AutoWIG/master"><img src="https://landscape.io/github/VirtualPlants/AutoWIG/master/landscape.svg?style=flat" alt="Landscape" /></a> <a href="http://AutoWIG.readthedocs.io/en/latest"><img src="https://readthedocs.org/projects/AutoWIG/badge/?version=latest" alt="Read the Docs" /></a></p>
</dd>
</dl>
</blockquote>