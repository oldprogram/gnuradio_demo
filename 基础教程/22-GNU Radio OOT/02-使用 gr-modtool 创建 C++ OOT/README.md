### 一、前言

本教程介绍如何创建自定义 C++ 块并在流程图中使用它：

- 使用 gr_modtool 创建新的 C++ 块
- 修改 C++ .h 和 .cc 代码，使该块能够运行
- 修改 YAML 文件，以便 GRC 可以读取它
- 在流程图中安装并运行该块

OOT 模块是指不存在于 GNU Radio 源代码树中的 GNU Radio 组件。源代码树是指 GNU Radio 已提供的一组块。因此，OOT 块是自定义块，用于扩展 GNU Radio 所需的特定功能。OOT 块允许您自行维护代码，并在主代码之外添加其他功能。它们的功能可以用 Python 或 C++ 定义。它们的配置通过 yaml 文件进行描述。

上一篇教程《[使用 gr-modtool 创建 Python OOT][#6]》介绍了如何在 OOT 模块中创建 Python 块。本篇 C++ OOT 教程和之前的 Python 教程，在“四、创建 OOT 块”部分之前的部分是一样的（如果之前你已经做了这些操作，可以直接跳到 “四、创建 OOT 块” 部分）。

</br>

### 二、安装说明

本教程使用 Ubuntu 24.04 上的 GNU Radio 3.10.9.2 (Python 3.12.3) 编写，并使用[安装 Wiki 页面][#5]中的 Ubuntu PPA 安装。基本的 GNU Radio 安装步骤如下：

```
sudo apt-get install gnuradio
```

未附带编译和安装 OOT 模块所需的正确库。请考虑在继续操作之前安装以下软件包：

```
sudo apt-get install gnuradio-dev cmake libspdlog-dev clang-format doxygen
```

</br>

### 三、创建 OOT 模块

打开终端并导航到用于编写软件的适当目录，例如主目录：

```
cd $HOME
```

GNU Radio 自带了 `gr_modtool`，这是一个用于创建树外 (OOT) 模块的软件工具。OOT 模块可以看作是自定义 GNU Radio 模块的集合。使用 `gr_modtool` 创建一个名为 `customModule` 的 OOT 模块：

```
gr_modtool newmod customModule
```

目录 `gr-customModule` 已创建，其中包含 OOT 模块的所有框架代码，但尚无任何块。进入 `gr-customModule` 目录：

```
cd gr-customModule
```

```
➜  gr-customModule tree
├── apps
│   └── CMakeLists.txt
├── cmake
│   ├── cmake_uninstall.cmake.in
│   └── Modules
│       └── CMakeParseArgumentsCopy.cmake/gnuradio-customModuleConfig.cmake/targetConfig.cmake.in
├── CMakeLists.txt
├── docs
│   ├── doxygen
│   │   ├── doxyxml
│   │   │   ├── generated
│   │   │   │   └── compound.py/compoundsuper.py/index.py/indexsuper.py/__init__.py
│   │   │   └── base.py/doxyindex.py/__init__.py/text.py
│   │   ├── other
│   │   │   └── doxypy.py/group_defs.dox/main_page.dox
│   │   └── CMakeLists.txt/Doxyfile.in/pydoc_macros.h/update_pydoc.py
│   └── CMakeLists.txt/README.customModule
├── examples
│   └── README
├── grc
│   └── CMakeLists.txt
├── include
│   └── gnuradio
│       └── customModule
│           └── api.h/CMakeLists.txt
├── lib
│   └── CMakeLists.txt
├── MANIFEST.md
└── python
    └── customModule
        ├── bindings
        │   ├── docstrings
        │   │   └── README.md
        │   └── CMakeLists.txt/bind_oot_file.py/header_utils.py/python_bindings.cc/README.md
        └── CMakeLists.txt/__init__.py

19 directories, 38 files
```

</br>

### 四、创建 OOT 块

现在需要在 `gr-customModule` 中创建一个块：

```
gr_modtool add multDivSelect
```

该命令将启动一个关于如何定义块的配置询问：[块类型][#4]、语言和参数：

```
➜  gr-customModule gr_modtool add multDivSelect
GNU Radio module name identified: customModule
('sink', 'source', 'sync', 'decimator', 'interpolator', 'general', 'tagged_stream', 'hier', 'noblock')
Enter block type: sync                                  # 选择同步块，它为每个输入产生一个输出
Language (python/cpp): cpp                              # cpp 作为语言
Language: C++
Block/code identifier: multDivSelect
Please specify the copyright holder: btfz               # 版权持有者的姓名或组织
Enter valid argument list, including default arguments: # 输入参数列表
 bool selector=true
Add Python QA code? [Y/n] n                             # 是否需要 Python 质量保证 (QA) 代码  
Add C++ QA code? [Y/n] n
Adding file 'lib/multDivSelect_impl.h'...               # 生成新文件 
Adding file 'lib/multDivSelect_impl.cc'...
Adding file 'include/gnuradio/customModule/multDivSelect.h'...
Adding file 'python/customModule/bindings/docstrings/multDivSelect_pydoc_template.h'...
Adding file 'python/customModule/bindings/multDivSelect_python.cc'...
Adding file 'grc/customModule_multDivSelect.block.yml'...
Editing grc/CMakeLists.txt...
```

</br>

### 五、修改 C++ impl.h 头文件

许多文件是自动生成的包装器代码，无需修改。但是 `multDivSelect_impl.h` 和 `multDivSelect_impl.cc` 定义了该块的操作，必须进行修改。

编辑 `lib/multDivSelect_impl.h`：

```
#ifndef INCLUDED_CUSTOMMODULE_MULTDIVSELECT_IMPL_H
#define INCLUDED_CUSTOMMODULE_MULTDIVSELECT_IMPL_H

#include <gnuradio/customModule/multDivSelect.h>

namespace gr {
namespace customModule {

class multDivSelect_impl : public multDivSelect
{
private:
    // Nothing to declare in this block.

public:
    multDivSelect_impl(bool selector);
    ~multDivSelect_impl();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace customModule
} // namespace gr

#endif /* INCLUDED_CUSTOMMODULE_MULTDIVSELECT_IMPL_H */
```

创建一个布尔私有成员 `_selector`，它将保存选择器参数的值：

```
class multDivSelect_impl : public multDivSelect
{
private:
    bool _selector;
```

</br>

### 六、修改 C++ impl.cc 文件

需要修改 .cc 文件以定义块所需的操作，打开 `lib/multDivSelect_impl.cc`：

```
#include "multDivSelect_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace customModule {

#pragma message("set the following appropriately and remove this warning")
using input_type = float;
#pragma message("set the following appropriately and remove this warning")
using output_type = float;
multDivSelect::sptr multDivSelect::make(bool selector)
{
    return gnuradio::make_block_sptr<multDivSelect_impl>(selector);
}


/*
 * The private constructor
 */
multDivSelect_impl::multDivSelect_impl(bool selector)
    : gr::sync_block("multDivSelect",
                     gr::io_signature::make(
                         1 /* min inputs */, 1 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(
                         1 /* min outputs */, 1 /*max outputs */, sizeof(output_type)))
{
}

/*
 * Our virtual destructor.
 */
multDivSelect_impl::~multDivSelect_impl() {}

int multDivSelect_impl::work(int noutput_items,
                             gr_vector_const_void_star& input_items,
                             gr_vector_void_star& output_items)
{
    auto in = static_cast<const input_type*>(input_items[0]);
    auto out = static_cast<output_type*>(output_items[0]);

#pragma message("Implement the signal processing in your block and remove this warning")
    // Do <+signal processing+>

    // Tell runtime system how many output items we produced.
    return noutput_items;
}

} /* namespace customModule */
} /* namespace gr */
```

删除 `#pragma message` 消息并将输入和输出类型定义为 gr_complex：

```
using input_type = gr_complex;
using output_type = gr_complex;
```

更新为两个输入并使用 `multDivSelector_impl.h` 中定义的私有成员 `_selector` 存储选择器参数的值：

```
multDivSelect_impl::multDivSelect_impl(bool selector)
    : gr::sync_block("multDivSelect",
                     gr::io_signature::make(
                         2 /* min inputs */, 2 /* max inputs */, sizeof(input_type)),
                     gr::io_signature::make(
                         1 /* min outputs */, 1 /*max outputs */, sizeof(output_type)))
{
    _selector = selector;
}
```

修改 `work()` 函数，删除 `#pragma message` 消息，定义与两个输入端口对应的变量 `in0` 和 `in1` ，如果 `_selector` 为真，则将两个输入相乘，如果 `_selector` 为假， 则将两个输入相除：

```
int multDivSelect_impl::work(int noutput_items,
                               gr_vector_const_void_star& input_items,
                               gr_vector_void_star& output_items)
{
    auto in0 = static_cast<const input_type*>(input_items[0]);
    auto in1 = static_cast<const input_type*>(input_items[1]);
    auto out = static_cast<output_type*>(output_items[0]);

    for (int index = 0; index < noutput_items; index++) {
        if (_selector) { out[index] = in0[index] * in1[index]; }
        else{ out[index] = in0[index] / in1[index]; }
    }

    // Tell runtime system how many output items we produced.
    return noutput_items;
}
```

</br>

### 七、修改 YAML.yml 文件

gnuradio-companion 使用 YAML（另一种标记语言）格式的文件来了解我们的 OOT 块以及如何调用它。有关此类文件的更多信息，请参阅 [YAML GRC][#5] 页面。

我们将 `grc/customModule_multDivSelect.block.yml` 修改为：

```
id: customModule_multDivSelect
label: multDivSelect
category: '[customModule]'

templates:
  imports: from gnuradio import customModule
  make: customModule.multDivSelect(${selector})

parameters:
- id: selector
  label: Selector, Multiply (true) or Divide (false)
  dtype: bool
  default: true

inputs:
- label: in0
  domain: stream
  dtype: complex
- label: in1
  domain: stream
  dtype: complex

outputs:
- label: out0
  domain: stream
  dtype: complex

file_format: 1
```

</br>

### 八、编译并安装块

进入 `gr_customModule` 顶层目录中：

```
rm -rf build
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig 
```

</br>

### 九、在流程图中使用自定义块

启动 GNU Radio Companion (GRC)：

```
gnuradio-companion &
```

运行效果如下：

![][p3]


</br>

### 十、改变

建议每次发生更改时都重新编译并重新安装模块，然后在 GRC 中重新加载块库。这包括以下更改：

- 参数数量
- 参数类型
- 输入端口或输出端口的数量
- 输入端口或输出端口的类型
- 修改 YAML .yml 文件
- 修改任何 C++ .h 或 .cc 文件

根据更改的范围，在重新编译和重新安装模块之前可能需要 删除并重新创建 `build/` 目录：

```
rm -rf gr-customModule/build 
mkdir gr-customModule/build
```

[#4]:https://wiki.gnuradio.org/index.php?title=Types_of_Blocks      
[#5]:https://wiki.gnuradio.org/index.php?title=YAML_GRC    
[#6]:https://github.com/oldprogram/gnuradio_demo/blob/main/%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B/22-GNU%20Radio%20OOT/01-%E4%BD%BF%E7%94%A8%20gr-modtool%20%E5%88%9B%E5%BB%BA%20Python%20OOT/README.md    

[p3]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/oot_multDivBlock_show.gif    

