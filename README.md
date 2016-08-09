<div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">
           <div itemprop="articleBody">
            
  <span class="target" id="module-autowig"><span id="autowig"></span></span><div class="section" id="autowig-automatic-wrapper-and-interface-generator">
<h1>AutoWIG: Automatic Wrapper and Interface Generator<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#autowig-automatic-wrapper-and-interface-generator" title="Permalink to this headline">&#182;</a></h1>
<p>High-level programming languages, like <em>Python</em> and <em>R</em>, are popular among scientists.
They tend to be concise and readable, leading to a rapid development cycle, but suffer from performance drawback compare to compiled language.
However, these languages allow to interface <em>C</em>, <em>C++</em> and <em>Fortran</em> code.
By this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries.
While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming.
In this paper, we introduce <strong>AutoWIG</strong>, a <em>Python</em> library that wraps automatically <em>C++</em> libraries into high-level languages.
Our solution consists in parsing <em>C++</em>  code using <strong>LLVM</strong>/<strong>CLang</strong> technology and generating the wrappers using the <strong>Mako</strong> templating engine.
Our approach is automatic, extensible, and can scale from simple <em>C++</em> libraries to very complex ones, composed of thousands of classes or using modern meta-programming constructs.
The usage and extension of <strong>AutoWIG</strong> is also illustrated on a set of statistical libraries.</p>
<div class="sidebar">
<p class="first sidebar-title">Summary</p>
<table class="last docutils field-list" frame="void" rules="none">
<col class="field-name">
<col class="field-body">
<tbody valign="top">
<tr class="field-odd field"><th class="field-name">Version:</th><td class="field-body">0.1.0</td>
</tr>
<tr class="field-even field"><th class="field-name">Release:</th><td class="field-body">0.1.0</td>
</tr>
<tr class="field-odd field"><th class="field-name">Date:</th><td class="field-body">June 30, 2016</td>
</tr>
<tr class="field-even field"><th class="field-name">Status:</th><td class="field-body"><a class="reference external" href="https://travis-ci.org/VirtualPlants/AutoWIG"><img alt="Travis" src="https://travis-ci.org/VirtualPlants/AutoWIG.svg?branch=master"></a> <a class="reference external" href="https://coveralls.io/github/VirtualPlants/AutoWIG?branch=master"><img alt="Coveralls" src="https://coveralls.io/repos/github/VirtualPlants/AutoWIG/badge.svg?branch=master"></a> <a class="reference external" href="https://landscape.io/github/VirtualPlants/AutoWIG/master"><img alt="Landscape" src="https://landscape.io/github/VirtualPlants/AutoWIG/master/landscape.svg?style=flat"></a> <a class="reference external" href="http://AutoWIG.readthedocs.io/en/latest"><img alt="Read the Docs" src="https://readthedocs.org/projects/AutoWIG/badge/?version=latest"></a></td>
</tr>
<tr class="field-odd field"><th class="field-name">Author:</th><td class="field-body">See <a class="reference internal" href="http://autowig.readthedocs.io/en/latest/#authors">Authors</a> section</td>
</tr>
</tbody>
</table>
</div>
<div class="section" id="documentation">
<h2>Documentation<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#documentation" title="Permalink to this headline">&#182;</a></h2>
<div class="toctree-wrapper compound">
<ul>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/install.html">Installation from sources</a><ul>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/install.html#requirements">Requirements</a></li>
</ul>
</li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/motivating_example.html">Motivating example</a></li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html">Methodology</a><ul>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html#an-interactive-workflow">An interactive workflow</a></li>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html#integrated-workflows">Integrated workflows</a></li>
</ul>
</li>
</ul>
</div>
</div>
<div class="section" id="authors">
<h2>Authors<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#authors" title="Permalink to this headline">&#182;</a></h2>
</div>
<div class="section" id="license">
<h2>License<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#license" title="Permalink to this headline">&#182;</a></h2>
<p><strong>AutoWIG</strong> is distributed under the <a class="reference external" href="http://autowig.readthedocs.io/en/latest/license.html">CeCILL-C license</a>.</p>
<div class="admonition note">
<p class="first admonition-title">Note</p>
<p class="last"><a class="reference external" href="http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html">Cecill-C</a>
license is a LGPL compatible license.</p>
</div>
</div>
</div>


           </div>
          </div>
