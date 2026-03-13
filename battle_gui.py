import io
import tkinter as tk
from contextlib import redirect_stdout
from tkinter import messagebox, ttk

import battle_character
import battle_system


CHARACTER_TYPES = {
    "Berserker": battle_character.Berserker,
    "Vampire": battle_character.Vampire,
    "Knight": battle_character.Knight,
    "DragonHuman": battle_character.DragonHuman,
    "FlameWitch": battle_character.FlameWitch,
    "Mermaid": battle_character.Mermaid,
    "WolfMan": battle_character.WolfMan,
    "Druid": battle_character.Druid,
    "SnowElf": battle_character.SnowElf,
}


def create_character(role_name: str, name: str, level: int):
    cls = CHARACTER_TYPES[role_name]
    return cls(name, level=level)


class BattleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Battle Simulator")
        self.geometry("980x640")
        self.minsize(900, 560)

        self.current_battle = None
        self.battle_active = False
        self.manual_actor = None
        self.manual_opponent = None
        self.waiting_manual_input = False

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="角色对战模拟器", font=("Microsoft YaHei UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        config_frame = ttk.LabelFrame(self, text="对战配置")
        config_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)

        self._build_player_panel(config_frame, "左侧角色", 0)
        self._build_player_panel(config_frame, "右侧角色", 1)

        settings = ttk.Frame(config_frame)
        settings.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 10))

        ttk.Label(settings, text="获胜奖励等级:").grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.reward_var = tk.IntVar(value=1)
        reward_spin = ttk.Spinbox(settings, from_=0, to=20, width=8, textvariable=self.reward_var)
        reward_spin.grid(row=0, column=1, sticky="w")

        self.verbose_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="显示详细日志", variable=self.verbose_var).grid(
            row=0, column=2, padx=(16, 0), sticky="w"
        )

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.rowconfigure(1, weight=1)

        tool_bar = ttk.Frame(btn_frame)
        tool_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        start_btn = ttk.Button(tool_bar, text="开始对战", command=self.run_battle)
        start_btn.pack(side="left")

        self.next_turn_btn = ttk.Button(tool_bar, text="执行下一回合", command=self.run_manual_turn, state="disabled")
        self.next_turn_btn.pack(side="left", padx=8)

        clear_btn = ttk.Button(tool_bar, text="清空日志", command=self.clear_log)
        clear_btn.pack(side="left", padx=8)

        skill_desc_btn = ttk.Button(tool_bar, text="查看技能描述", command=self.show_skill_descriptions)
        skill_desc_btn.pack(side="left", padx=8)

        self.winner_label = ttk.Label(tool_bar, text="胜者: -", font=("Microsoft YaHei UI", 10, "bold"))
        self.winner_label.pack(side="right")

        battle_area = ttk.Frame(btn_frame)
        battle_area.grid(row=1, column=0, columnspan=2, sticky="nsew")
        battle_area.columnconfigure(0, weight=1)
        battle_area.rowconfigure(0, weight=1)

        log_frame = ttk.Frame(battle_area)
        log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap="word", font=("Consolas", 11))
        self.log_text.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=y_scroll.set)

        status_panel = ttk.LabelFrame(battle_area, text="角色状态")
        status_panel.grid(row=0, column=1, sticky="ns")
        status_panel.rowconfigure(0, weight=1)
        status_panel.rowconfigure(1, weight=1)
        status_panel.columnconfigure(0, weight=1)

        p1_status_frame = ttk.LabelFrame(status_panel, text="左侧角色")
        p1_status_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")
        p1_status_frame.columnconfigure(0, weight=1)
        p1_status_frame.rowconfigure(0, weight=1)
        self.p1_status_text = tk.Text(p1_status_frame, wrap="word", width=36, height=10, font=("Consolas", 10))
        self.p1_status_text.grid(row=0, column=0, padx=(8, 0), pady=8, sticky="nsew")
        p1_scroll = ttk.Scrollbar(p1_status_frame, orient="vertical", command=self.p1_status_text.yview)
        p1_scroll.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="ns")
        self.p1_status_text.configure(yscrollcommand=p1_scroll.set)
        self.p1_status_text.configure(state="disabled")

        p2_status_frame = ttk.LabelFrame(status_panel, text="右侧角色")
        p2_status_frame.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="ew")
        p2_status_frame.columnconfigure(0, weight=1)
        p2_status_frame.rowconfigure(0, weight=1)
        self.p2_status_text = tk.Text(p2_status_frame, wrap="word", width=36, height=10, font=("Consolas", 10))
        self.p2_status_text.grid(row=0, column=0, padx=(8, 0), pady=8, sticky="nsew")
        p2_scroll = ttk.Scrollbar(p2_status_frame, orient="vertical", command=self.p2_status_text.yview)
        p2_scroll.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="ns")
        self.p2_status_text.configure(yscrollcommand=p2_scroll.set)
        self.p2_status_text.configure(state="disabled")

        manual_panel = ttk.LabelFrame(btn_frame, text="手动回合控制")
        manual_panel.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))

        self.turn_info_label = ttk.Label(manual_panel, text="当前回合角色: -")
        self.turn_info_label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        ttk.Label(manual_panel, text="选择技能:").grid(row=0, column=1, padx=(8, 4), pady=8, sticky="w")
        self.manual_skill_var = tk.StringVar(value="")
        self.manual_skill_combo = ttk.Combobox(
            manual_panel,
            textvariable=self.manual_skill_var,
            values=[],
            state="disabled",
            width=30,
        )
        self.manual_skill_combo.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        self.clear_log()

    def _special_status_lines(self, char):
        status_lines = []
        debuff_lines = []
        skill_lines = []
        runtime_status = {}
        if hasattr(char, "get_runtime_status"):
            try:
                runtime_status = char.get_runtime_status() or {}
            except Exception:
                runtime_status = {}

        skill_runtime = runtime_status.get("skill_runtime", {}) if isinstance(runtime_status, dict) else {}
        debuffs = runtime_status.get("debuffs", []) if isinstance(runtime_status, dict) else []

        # 角色独立状态（不属于技能描述）
        if hasattr(char, "rage"):
            status_lines.append(f"rage: {int(getattr(char, 'rage', 0))}")
        if hasattr(char, "dragon_breath") and hasattr(char, "max_dragon_breath"):
            status_lines.append(f"dragon_breath: {int(char.dragon_breath)}/{int(char.max_dragon_breath)}")
        if hasattr(char, "MP") and hasattr(char, "maxMP"):
            status_lines.append(f"MP: {int(char.MP)}/{int(char.maxMP)}")
        if hasattr(char, "shield"):
            status_lines.append(f"shield: {int(getattr(char, 'shield', 0))}")
        if hasattr(char, "bat_count"):
            status_lines.append(f"bat_count: {int(getattr(char, 'bat_count', 0))}")
        if hasattr(char, "summons_on_field"):
            summons = ", ".join(char.summons_on_field) if char.summons_on_field else "none"
            status_lines.append(f"summons: {summons}")
        if hasattr(char, "treant_max_hp") and getattr(char, "summons", {}).get("treant", False):
            status_lines.append(f"treant_hp: {int(getattr(char, 'treant_max_hp', 0))}")

        # 特殊状态
        if hasattr(char, "rage_flag") and bool(getattr(char, "rage_flag", False)):
            status_lines.append(f"state: rage({int(getattr(char, 'rage_buff_turns', 0))})")
        if hasattr(char, "wolf_evolution_flag") and bool(getattr(char, "wolf_evolution_flag", False)):
            status_lines.append("state: wolf_form")
        if hasattr(char, "counterattack_active") and bool(getattr(char, "counterattack_active", False)):
            status_lines.append(f"state: counter_stance({int(getattr(char, 'counterattack_active_turns', 0))})")
        if hasattr(char, "tree_spirit_blessing_active") and bool(getattr(char, "tree_spirit_blessing_active", False)):
            status_lines.append(f"state: tree_blessing({int(getattr(char, 'tree_spirit_blessing_turns', 0))})")
        if hasattr(char, "attack_buff_flag") and bool(getattr(char, "attack_buff_flag", False)):
            status_lines.append(f"state: dragon_attack_up({int(getattr(char, 'attack_buff_turns', 0))})")

        # 负面状态明细（有效值，剩余回合）
        if debuffs:
            for item in debuffs:
                debuff_lines.append(str(item))

        if skill_runtime:
            for skill_name, text in skill_runtime.items():
                text_str = str(text)
                # 展示技能冷却与可用次数
                if any(key in text_str for key in ("cd=", "remaining=", "charges=")):
                    skill_lines.append(f"{skill_name}: {text_str}")

        lines = []
        lines.append("[角色状态]")
        if status_lines:
            lines.extend(status_lines)
        else:
            lines.append("无")

        lines.append("")
        lines.append("[Debuff明细]")
        if debuff_lines:
            lines.extend(debuff_lines)
        else:
            lines.append("无")

        lines.append("")
        lines.append("[技能CD/次数]")
        if skill_lines:
            lines.extend(skill_lines)
        else:
            lines.append("无技能CD或次数限制")
        return lines

    def _set_status_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _format_skill_description_for_role(self, role_name, preview_name, level):
        try:
            char = create_character(role_name, preview_name, level)
            descriptions = char.get_skill_descriptions()
        except Exception as exc:
            return f"[{role_name}] 技能读取失败: {exc}\n"

        lines = [f"[{role_name}] 技能说明"]
        for skill_name in char.skills.keys():
            desc = descriptions.get(skill_name, "暂无描述")
            lines.append(f"- {skill_name}: {desc}")
        return "\n".join(lines) + "\n"

    def show_skill_descriptions(self):
        left_text = self._format_skill_description_for_role(
            self.p1_role.get(),
            self.p1_name.get().strip() or "P1",
            int(self.p1_level.get()),
        )
        right_text = self._format_skill_description_for_role(
            self.p2_role.get(),
            self.p2_name.get().strip() or "P2",
            int(self.p2_level.get()),
        )

        window = tk.Toplevel(self)
        window.title("技能描述")
        window.geometry("760x520")

        text = tk.Text(window, wrap="word", font=("Microsoft YaHei UI", 10))
        text.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        scroll.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll.set)

        text.insert("1.0", left_text + "\n" + right_text)
        text.configure(state="disabled")

    def _format_status_text(self, char, role_name):
        base = [
            f"name: {char.name}",
            f"class: {role_name}",
            f"level: {char.level}",
            f"HP: {int(char.health)}/{int(char.maxHP)}",
        ]
        return "\n".join(base + self._special_status_lines(char))

    def _update_status_panel(self, char1=None, char2=None):
        if self.current_battle is not None:
            char1 = self.current_battle.char1
            char2 = self.current_battle.char2

        if char1 is None or char2 is None:
            self._set_status_text(self.p1_status_text, "未开始战斗")
            self._set_status_text(self.p2_status_text, "未开始战斗")
            return

        self._set_status_text(self.p1_status_text, self._format_status_text(char1, self.p1_role.get()))
        self._set_status_text(self.p2_status_text, self._format_status_text(char2, self.p2_role.get()))

    def _build_player_panel(self, parent, title, column):
        panel = ttk.LabelFrame(parent, text=title)
        panel.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        panel.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(panel, text="名字:").grid(row=row, column=0, sticky="w", padx=6, pady=6)
        name_var = tk.StringVar(value=f"Player{column + 1}")
        name_entry = ttk.Entry(panel, textvariable=name_var)
        name_entry.grid(row=row, column=1, sticky="ew", padx=6, pady=6)

        row += 1
        ttk.Label(panel, text="职业:").grid(row=row, column=0, sticky="w", padx=6, pady=6)
        role_var = tk.StringVar(value="Berserker" if column == 0 else "FlameWitch")
        role_combo = ttk.Combobox(panel, textvariable=role_var, values=list(CHARACTER_TYPES.keys()), state="readonly")
        role_combo.grid(row=row, column=1, sticky="ew", padx=6, pady=6)

        row += 1
        ttk.Label(panel, text="等级:").grid(row=row, column=0, sticky="w", padx=6, pady=6)
        level_var = tk.IntVar(value=1)
        level_spin = ttk.Spinbox(panel, from_=1, to=60, textvariable=level_var, width=8)
        level_spin.grid(row=row, column=1, sticky="w", padx=6, pady=6)

        row += 1
        ttk.Label(panel, text="操作:").grid(row=row, column=0, sticky="w", padx=6, pady=6)
        mode_var = tk.StringVar(value="manual" if column == 0 else "auto")
        mode_frame = ttk.Frame(panel)
        mode_frame.grid(row=row, column=1, sticky="w", padx=6, pady=6)
        ttk.Radiobutton(mode_frame, text="手动", value="manual", variable=mode_var).pack(side="left")
        ttk.Radiobutton(mode_frame, text="自动", value="auto", variable=mode_var).pack(side="left", padx=(8, 0))

        if column == 0:
            self.p1_name = name_var
            self.p1_role = role_var
            self.p1_level = level_var
            self.p1_mode = mode_var
        else:
            self.p2_name = name_var
            self.p2_role = role_var
            self.p2_level = level_var
            self.p2_mode = mode_var

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, "准备就绪，点击【开始对战】执行模拟。\n")
        self.log_text.see(tk.END)

    def append_log(self, text: str):
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)

    def _validate_inputs(self):
        p1_name = self.p1_name.get().strip()
        p2_name = self.p2_name.get().strip()
        if not p1_name or not p2_name:
            raise ValueError("角色名字不能为空")

        p1_level = int(self.p1_level.get())
        p2_level = int(self.p2_level.get())
        if p1_level < 1 or p2_level < 1:
            raise ValueError("等级必须大于等于 1")
        elif p1_level > 60 or p2_level > 60:
            raise ValueError("等级不能超过 60")

        return p1_name, p2_name, p1_level, p2_level

    def _create_battle_from_inputs(self):
        p1_name, p2_name, p1_level, p2_level = self._validate_inputs()
        char1 = create_character(self.p1_role.get(), p1_name, p1_level)
        char2 = create_character(self.p2_role.get(), p2_name, p2_level)
        bs = battle_system.BattleSystem(char1, char2)
        return bs, char1, char2

    def _set_manual_controls(self, enabled: bool):
        self.next_turn_btn.configure(state="normal" if enabled else "disabled")
        self.manual_skill_combo.configure(state="readonly" if enabled else "disabled")

    def _get_actor_mode(self, actor):
        if self.current_battle is None:
            return "auto"
        if actor is self.current_battle.char1:
            return self.p1_mode.get()
        return self.p2_mode.get()

    def _evaluate_winner(self):
        if self.current_battle is None:
            return None
        bs = self.current_battle
        if bs.char1.is_alive() and not bs.char2.is_alive():
            return bs.char1
        if bs.char2.is_alive() and not bs.char1.is_alive():
            return bs.char2
        if bs.turn >= 100:
            return None
        return None

    def _finish_battle(self, winner):
        bs = self.current_battle
        if winner is not None:
            if self.verbose_var.get():
                self.append_log(f"\n=== {winner.name} 获胜！===\n")
            reward_levels = max(0, int(self.reward_var.get()))
            if reward_levels > 0:
                if self.verbose_var.get():
                    self.append_log(f"{winner.name} 战后获得 {reward_levels} 级奖励！\n")
                log_stream = io.StringIO()
                with redirect_stdout(log_stream):
                    winner.gain_levels(reward_levels, announce=self.verbose_var.get())
                    winner.settlement()
                extra_logs = log_stream.getvalue()
                if extra_logs.strip():
                    self.append_log(extra_logs)
            winner_name = winner.name
        else:
            self.append_log("\n=== 平局（达到回合上限或双方同时倒下）===\n")
            winner_name = "平局"

        self.winner_label.configure(text=f"胜者: {winner_name}")
        if bs is not None:
            self._update_status_panel(bs.char1, bs.char2)
        self.battle_active = False
        self.current_battle = None
        self.manual_actor = None
        self.manual_opponent = None
        self.waiting_manual_input = False
        self.turn_info_label.configure(text="当前回合角色: -")
        self.manual_skill_combo["values"] = []
        self.manual_skill_var.set("")
        self._set_manual_controls(False)

    def _prepare_manual_turn(self):
        if self.current_battle is None:
            return

        bs = self.current_battle
        if not bs.char1.is_alive() or not bs.char2.is_alive() or bs.turn >= 100:
            if bs.char1.is_alive() and not bs.char2.is_alive():
                winner = bs.char1
            elif bs.char2.is_alive() and not bs.char1.is_alive():
                winner = bs.char2
            else:
                winner = None
            self._finish_battle(winner)
            return

        actor = bs.char1 if bs.turn % 2 == 0 else bs.char2
        opponent = bs.char2 if actor is bs.char1 else bs.char1
        available_skills = actor.get_available_skills()
        if not available_skills:
            available_skills = ["attack"]

        self.manual_actor = actor
        self.manual_opponent = opponent
        self.turn_info_label.configure(
            text=f"第 {bs.turn + 1} 回合: {actor.name} -> {opponent.name}"
        )
        self.manual_skill_combo["values"] = available_skills
        self.manual_skill_var.set(available_skills[0])
        self._set_manual_controls(True)
        self.waiting_manual_input = True

    def _execute_turn(self, actor, opponent, forced_skill_name=None):
        bs = self.current_battle
        if bs is None:
            return

        if forced_skill_name is None:
            call_name, args, kwargs = battle_system.default_strategy(actor, opponent)
        else:
            call_name, args, kwargs = battle_system.build_skill_call(actor, forced_skill_name, opponent)

        log_stream = io.StringIO()
        with redirect_stdout(log_stream):
            actor.on_turn_start()
            if not actor.can_act():
                if self.verbose_var.get():
                    print(f"\n第 {bs.turn + 1} 回合：{actor.name} 因控制效果跳过行动")
            else:
                if self.verbose_var.get():
                    print(f"\n第 {bs.turn + 1} 回合：{actor.name} 使用了技能 '{call_name}'")
                try:
                    actor.use_skill(call_name, *args, **kwargs)
                except Exception as exc:
                    if self.verbose_var.get():
                        print(f"{actor.name} 无法使用技能 {call_name}：{exc}")
            bs.turn += 1

        logs = log_stream.getvalue()
        if logs.strip():
            self.append_log(logs)
        self._update_status_panel()

    def _advance_until_manual_or_end(self, manual_skill_name=None):
        if self.current_battle is None:
            return

        used_manual_skill = False
        while self.current_battle is not None:
            bs = self.current_battle
            if (not bs.char1.is_alive()) or (not bs.char2.is_alive()) or bs.turn >= 100:
                winner = self._evaluate_winner()
                self._finish_battle(winner)
                return

            actor = bs.char1 if bs.turn % 2 == 0 else bs.char2
            opponent = bs.char2 if actor is bs.char1 else bs.char1
            actor_mode = self._get_actor_mode(actor)

            if actor_mode == "manual" and not used_manual_skill:
                if manual_skill_name is None:
                    self.manual_actor = actor
                    self.manual_opponent = opponent
                    self._prepare_manual_turn()
                    return
                skill_name = manual_skill_name
                available_skills = actor.get_available_skills()
                if skill_name not in available_skills:
                    skill_name = "attack"
                self.waiting_manual_input = False
                self._execute_turn(actor, opponent, forced_skill_name=skill_name)
                manual_skill_name = None
                used_manual_skill = True
            elif actor_mode == "manual" and used_manual_skill:
                self.manual_actor = actor
                self.manual_opponent = opponent
                self._prepare_manual_turn()
                return
            else:
                self.waiting_manual_input = False
                self._execute_turn(actor, opponent)

    def start_battle(self):
        try:
            bs, char1, char2 = self._create_battle_from_inputs()
        except Exception as exc:
            messagebox.showerror("创建角色失败", str(exc))
            return

        self.current_battle = bs
        self.battle_active = True
        self.winner_label.configure(text="胜者: -")

        self.clear_log()
        self.append_log(
            f"开始战斗: {char1.name}({self.p1_role.get()} Lv{char1.level}, {self.p1_mode.get()}) vs "
            f"{char2.name}({self.p2_role.get()} Lv{char2.level}, {self.p2_mode.get()})\n\n"
        )
        self._update_status_panel(char1, char2)
        self._advance_until_manual_or_end()

    def run_manual_turn(self):
        if not self.battle_active or self.current_battle is None:
            messagebox.showinfo("提示", "请先点击开始对战")
            return
        if not self.waiting_manual_input or self.manual_actor is None:
            messagebox.showinfo("提示", "当前回合为自动执行方，无需手动选择")
            return

        skill_name = self.manual_skill_var.get().strip() or "attack"
        self._advance_until_manual_or_end(manual_skill_name=skill_name)

    def run_battle(self):
        self.battle_active = False
        self.current_battle = None
        self.manual_actor = None
        self.manual_opponent = None
        self.waiting_manual_input = False
        self._set_manual_controls(False)
        self.turn_info_label.configure(text="当前回合角色: -")
        self.manual_skill_combo["values"] = []
        self.manual_skill_var.set("")
        self._update_status_panel(None, None)
        self.start_battle()


def main():
    app = BattleApp()
    app.mainloop()


if __name__ == "__main__":
    main()
