"""环境检测：GPU / Python / 依赖包 / 模型缓存"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "SmilingWolf/wd-vit-tagger-v3"
FILES = ["model.onnx", "selected_tags.csv"]


def detect_gpu():
    """返回 [(名称, 显存MB或''), ...]；跨平台尽力而为"""
    gpus = []
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-c",
             "Get-CimInstance Win32_VideoController | ForEach-Object { \"$($_.Name)|$([math]::Round($_.AdapterRAM/1MB))\" }"],
            capture_output=True, text=True, timeout=15)
        for line in r.stdout.strip().splitlines():
            if "|" in line:
                name, mem = line.split("|", 1)
                gpus.append((name.strip(), mem if mem not in ("0", "") else "?"))
    except Exception:
        pass
    if not gpus:
        try:
            r = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                               capture_output=True, text=True, timeout=8)
            gpus = [(l.strip(), "") for l in r.stdout.strip().splitlines() if l.strip()]
        except Exception:
            gpus = [("未检测到独立 GPU（可使用 CPU / 核显 DirectML）", "")]
    return gpus


def check_package(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def _installed_dist_names() -> set:
    """包发行名集合（onnxruntime-directml 的导入名是 onnxruntime，
    find_spec 查不到发行名，必须用 importlib.metadata 查）"""
    try:
        from importlib.metadata import distributions
        return {d.metadata["Name"].lower() for d in distributions()}
    except Exception:
        return set()


def check_dist(dist_name: str) -> bool:
    return dist_name.lower() in _installed_dist_names()


def check_providers() -> list:
    try:
        import onnxruntime as ort
        return ort.get_available_providers()
    except Exception:
        return []


def model_cached(model_dir: Path) -> bool:
    return all((model_dir / f).exists() for f in FILES)


def full_report(model_dir: Path):
    import platform
    d = _installed_dist_names()

    def installed(dist, import_name):
        # 双检测兜底：发行名枚举对个别包不可靠，导入名补充
        return dist in d or check_package(import_name)

    has_ort = installed("onnxruntime", "onnxruntime") or installed("onnxruntime-directml", "onnxruntime")
    rows = [
        ("操作系统", f"{platform.system()} {platform.release()}"),
        ("Python", sys.version.split()[0]),
        ("GPU", "; ".join(f"{n} ({m})" for n, m in detect_gpu()) or "未检测到"),
        ("onnxruntime", "已安装" if has_ort else "未安装"),
        ("onnxruntime-directml", "已安装" if "onnxruntime-directml" in d else "未安装（可选，装其一即可）"),
        ("PySide6", "已安装" if installed("pyside6", "PySide6") else "未安装"),
        ("huggingface_hub", "已安装" if installed("huggingface-hub", "huggingface_hub") else "未安装"),
        ("推理后端", ", ".join(check_providers()) or "onnxruntime 不可用"),
        ("WD14 模型", "已缓存" if model_cached(model_dir) else "未下载（下载约 400MB）"),
    ]
    return rows


def install_missing(pip_target: str = "", log=print):
    """一键安装缺失依赖；pip_target 指定 --target 目录（用户自定义安装位置）"""
    pkgs = ["PySide6", "numpy", "pillow", "huggingface_hub"]
    on_win = sys.platform == "win32"
    if check_dist("onnxruntime") or check_dist("onnxruntime-directml"):
        log("[INFO] onnxruntime 已存在，跳过")
    else:
        pkgs.append("onnxruntime-directml" if on_win else "onnxruntime")
    if shutil.which("pip") is None and shutil.which("pip3") is None:
        log("[FAIL] 未找到 pip，请确认 Python 环境")
        return False
    pip = sys.executable.replace("pythonw.exe", "python.exe") + " -m pip"
    for p in pkgs:
        if p in ("PySide6", "numpy", "pillow", "huggingface_hub") and check_package(
                {"PySide6": "PySide6", "numpy": "numpy", "pillow": "PIL", "huggingface_hub": "huggingface_hub"}[p]):
            log(f"[SKIP] {p} 已安装")
            continue
        cmd = f"{pip} install {p}"
        if pip_target:
            cmd += f' --target "{pip_target}"'
        log(f"[RUN ] {cmd}")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        ok = r.returncode == 0
        log(("[OK  ] " if ok else "[FAIL] ") + p + ("" if ok else "\n" + r.stderr[-500:]))
    return True


def download_model(model_dir: Path, log=print):
    """从 HuggingFace 下载 WD14 模型到 model_dir"""
    model_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        log("[FAIL] 缺少 huggingface_hub，请先安装依赖")
        return False
    for f in FILES:
        log(f"[DOWN] {REPO}/{f} ...")
        try:
            path = hf_hub_download(REPO, f, local_dir=model_dir)
            log(f"[OK  ] {path}")
        except Exception as e:
            log(f"[FAIL] {f}: {e}")
            return False
    return True
