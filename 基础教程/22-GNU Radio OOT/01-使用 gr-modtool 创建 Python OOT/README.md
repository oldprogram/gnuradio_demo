### 一、前言

本教程介绍如何创建自定义 Python 块或 Out-of-Tree (OOT) 模块并在流程图中使用它，步骤如下：

- 使用 gr_modtool 创建 OOT 模块
- 使用 gr_modtool 创建新的 Python 块
- 在文本编辑器中修改 Python 代码，使该块能够运行
- 修改 YAML 文件，以便它可以在 Gnuradio Companion (GRC) 中显示
- 在流程图中安装并运行该块

OOT 模块是指不存在于 GNU Radio 源代码树中的 GNU Radio 组件。源代码树是指 GNU Radio 已提供的一组块。因此，OOT 块是自定义块，用于扩展 GNU Radio 所需的特定功能。OOT 块允许您自行维护代码，并在主代码之外添加其他功能。它们的功能可以用 Python 或 C++ 定义。它们的配置通过 yaml 文件进行描述。

关于在 GRC 中使用嵌入式 Python 模块的教程，请参阅“[创建您的第一个模块][#1]”页面。此外，还有一些其他教程，[介绍如何使用标签][#2]、如何在 Python 模块中[传递消息][#3]以及[如何添加向量输入和输出][#4]，这些教程适用于嵌入式 Python 模块和 OOT Python 模块。

下一个教程《使用 gr-modtool 创建 C++ OOT》介绍了如何构建自定义 C++ OOT 模块。C++ OOT 教程基于 Python 教程，因此建议至少完成“创建 OOT 模块”部分后再继续学习。

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

其中包含的详细信息为：

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

现在需要在 `gr-customModule` 中创建一个块。该自定义块将根据输入参数进行加法或减法运算，因此该块名为 `addSubSelect`：

```
gr_modtool add addSubSelect
```

该命令将启动一个关于如何定义块的配置询问：块类型、语言和参数：

```
➜  gr-customModule gr_modtool add addSubSelect
GNU Radio module name identified: customModule
('sink', 'source', 'sync', 'decimator', 'interpolator', 'general', 'tagged_stream', 'hier', 'noblock')
Enter block type: sync                                  # 选择同步块，它为每个输入产生一个输出
Language (python/cpp): python                           # python 作为语言
Language: Python
Block/code identifier: addSubSelect
Please specify the copyright holder: btfz               # 版权持有者的姓名或组织
Enter valid argument list, including default arguments: # 输入参数列表
 selector=True
Add Python QA code? [Y/n] n                             # 是否需要 Python 质量保证 (QA) 代码  
Adding file 'python/customModule/addSubSelect.py'...    # 生成新文件
Adding file 'grc/customModule_addSubSelect.block.yml'...
Editing grc/CMakeLists.txt...
```

创建了两个新文件：`addSubSelect.py` 和 `customModule_addSubSelect.block.yml`，前者定义了模块的操作，后者定义了 GNU Radio Companion (GRC) 的模块接口。`CMakeLists.txt` 文件也进行了修改，以便在模块编译和安装时自动安装这两个文件。

**备注：** [块类型详细说明][#6]：

| 块类型（Category） | 中文名称 | 主要特点和功能 |
| :--- | :--- | :--- |
| **sink** | **接收器/终端** | - **数据流的终点**：用于接收和消耗流数据。 </br>- **无输出端口**：通常只有一个输入端口。 </br>- **例子**：将信号写入文件（`file_sink`）、发送到声卡（`audio_sink`）、显示图形（如示波器或瀑布图，`QT GUI Sink`）。 |
| **source** | **发送器/源** | - **数据流的起点**：用于生成流数据。 </br>- **无输入端口**：通常只有一个输出端口。 </br>- **例子**：从文件读取信号（`file_source`）、从硬件（如 USRP）接收信号、生成测试信号（如正弦波 `signal_source`）。 |
| **sync** | **同步块** | - **输入和输出采样率相同**：输入流中的一个样本对应输出流中的一个样本。 </br>- **$M$ 个输入样本 $\to$ $M$ 个输出样本**。 </br>- **例子**：简单的数学运算（如乘法、加法）、滤波器（没有抽取或插值的）、FFT/IFFT 块。 |
| **decimator** | **抽取块** | - **降低采样率**：输出采样率是输入采样率的 $1/D$ 倍，其中 $D$ 是抽取因子。 </br>- **$D \cdot M$ 个输入样本 $\to$ $M$ 个输出样本**。 </br>- **例子**：需要降低数据率的滤波器（`fir_filter_blk` with decimation）。 |
| **interpolator** | **插值块** | - **提高采样率**：输出采样率是输入采样率的 $I$ 倍，其中 $I$ 是插值因子。 </br>- **$M$ 个输入样本 $\to$ $I \cdot M$ 个输出样本**。 </br>- **例子**：需要提高数据率的滤波器（`fir_filter_blk` with interpolation）。 |
| **general** | **通用块** | - **最灵活的类型**：通常用于实现复杂的、采样率关系不固定的、或难以归入其他类别的算法。 </br>- **可以是同步、抽取、插值或混合操作**。 </br>- **需要开发者手动管理输入和输出数据的消耗与生产**。 </br>- **例子**：任何自定义的复杂处理块，例如解调器、解码器等。 |
| **tagged\_stream** | **带标签流块** | - **处理带标签的数据流**：数据流中包含“标签”（Tags），这些标签包含额外的信息（如时间戳、数据包边界、元数据）。 </br>- **处理逻辑依赖于标签**：块的操作可能受其接收到的标签影响。 </br>- **例子**：帧同步、数据包处理。 |
| **hier** | **层级块（Hierarchical Block）** | - **容器/子图**：本身不是执行信号处理的原子操作，而是将多个 GNU Radio 块封装成一个单一的、可重用的块。 </br>- **简化图表**：用于管理复杂流程图的结构，提高可读性和重用性。 </br>- **例子**：一个包含解调、解码、纠错等步骤的完整接收模块，可以被封装成一个层级块。 |
| **noblock** | **非流式块** | - **不参与流数据处理**：不连接到信号流，通常用于图形界面（GUI）的控制、参数设置或显示。 </br>- **没有输入/输出端口**：通过变量（Variables）或消息端口与其他块交互。 </br>- **例子**：滑块（`QT GUI Range`）、文本输入框、按钮、以及用于控制流图的**变量**。 |

</br>

### 五、修改 Python .py 文件

使用编辑器打开 `python/customModule/addSubSelect.py` 文件：

```
import numpy
from gnuradio import gr

class addSubSelect(gr.sync_block):
    """
    docstring for block addSubSelect
    """
    def __init__(self, selector=True):
        gr.sync_block.__init__(self,
            name="addSubSelect",
            in_sig=[<+numpy.float32+>, ],
            out_sig=[<+numpy.float32+>, ])


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        # <+signal processing here+>
        out[:] = in0
        return len(output_items[0])
```

修改为：

```
import numpy as np
from gnuradio import gr

class addSubSelect(gr.sync_block):
    """
    docstring for block addSubSelect
    """
    def __init__(self, selector=True):
        gr.sync_block.__init__(self,
                               name="addSubSelect",
                               in_sig=[np.complex64,np.complex64],
                               out_sig=[np.complex64])
        self.selector = selector

    def work(self, input_items, output_items):
        in0 = input_items[0]
        in1 = input_items[1]

        if (self.selector):
            output_items[0][:] = in0 + in1
        else:
            output_items[0][:] = in0 - in1

        return len(output_items[0])
```

**注意：** 需要将 `addSubSelect.py` 增加进 `python/customModule/CMakeLists.txt` 中的：

```
gr_python_install(FILES __init__.py addSubSelect.py DESTINATION ${GR_PYTHON_DIR}/gnuradio/customModule)
```

</br>

### 六、修改 YAML.yml 文件

使用编辑器打开 `grc/customModule_addSubSelect.block.yml` 文件：

```
id: customModule_addSubSelect
label: addSubSelect
category: '[customModule]'

templates:
  imports: from gnuradio import customModule
  make: customModule.addSubSelect(${selector})

#  Make one 'parameters' list entry for every parameter you want settable from the GUI.
#     Keys include:
#     * id (makes the value accessible as keyname, e.g. in the make entry)
#     * label (label shown in the GUI)
#     * dtype (e.g. int, float, complex, byte, short, xxx_vector, ...)
#     * default
parameters:
- id: parametername_replace_me
  label: FIX ME:
  dtype: string
  default: You need to fill in your grc/customModule_addSubSelect.block.yaml
#- id: ...
#  label: ...
#  dtype: ...

#  Make one 'inputs' list entry per input and one 'outputs' list entry per output.
#  Keys include:
#      * label (an identifier for the GUI)
#      * domain (optional - stream or message. Default is stream)
#      * dtype (e.g. int, float, complex, byte, short, xxx_vector, ...)
#      * vlen (optional - data stream vector length. Default is 1)
#      * optional (optional - set to 1 for optional inputs. Default is 0)
inputs:
#- label: ...
#  domain: ...
#  dtype: ...
#  vlen: ...
#  optional: ...

outputs:
#- label: ...
#  domain: ...
#  dtype: ...
#  vlen: ...
#  optional: ...

#  'file_format' specifies the version of the GRC yml format used in the file
#  and should usually not be changed.
file_format: 1
```

更改为：

```
id: customModule_addSubSelect
label: addSubSelect
category: '[customModule]'

templates:
  imports: from gnuradio import customModule
  make: customModule.addSubSelect(${selector})

parameters:
- id: selector
  label: Add (True) or Subtract (False) Selector
  dtype: bool
  default: True

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

### 七、编译并安装块

在 `gr_customModule` 顶层目录中创建 `build` 目录：

```
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig 
```
 
</br>

### 八、在流程图中使用自定义块

启动 GNU Radio Companion (GRC)：

```
gnuradio-companion &
```

![][p1]

运行效果如下：

![][p2]

</br>

### 九、改变

建议每次发生更改时都重新编译并重新安装模块，然后在 GRC 中重新加载块库。这包括以下更改：

- 参数数量
- 参数类型
- 输入端口或输出端口的数量
- 输入端口或输出端口的类型
- 修改 YAML.yml 文件
- 修改 Python.py 文件

根据更改的范围，在重新编译和重新安装模块之前可能需要 删除并重新创建 `build/` 目录：

```
rm -rf gr-customModule/build 
mkdir gr-customModule/build
```


[#1]:https://www.bilibili.com/video/BV18V4y1g7i9/?spm_id_from=333.788&vd_source=84f94348691c2906fc1038d54989b7e0      
[#2]:https://www.bilibili.com/video/BV1uW4y1v77Y/?spm_id_from=333.788&vd_source=84f94348691c2906fc1038d54989b7e0     
[#3]:https://www.bilibili.com/video/BV1DN4y1N7n1/?spm_id_from=333.788&vd_source=84f94348691c2906fc1038d54989b7e0      
[#4]:https://www.bilibili.com/video/BV1MB4y1n7od/?spm_id_from=333.788&vd_source=84f94348691c2906fc1038d54989b7e0        
[#5]:https://wiki.gnuradio.org/index.php?title=InstallingGR     
[#6]:https://wiki.gnuradio.org/index.php?title=Types_of_Blocks    

[p1]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/oot_addSubSelect_usage.gif     
[p2]:https://tuchuang.beautifulzzzz.com:3000/?path=202510/oot_addSubSelect_show.gif     
 