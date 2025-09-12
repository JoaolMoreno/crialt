import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {SharedModule} from "../../../shared/shared.module";

@Component({
    selector: 'app-stage-form',
    standalone: true,
    templateUrl: './stage-form.component.html',
    imports: [SharedModule],
    styleUrls: ['./stage-form.component.scss']
})
export class StageFormComponent implements OnInit {
  @Input() stage: any = {};
  @Output() save = new EventEmitter<any>();
  form!: FormGroup;
  escopoKeys: string[] = [];

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      name: [this.stage.name || '', Validators.required],
      description: [this.stage.description || ''],
      planned_start_date: [this.stage.planned_start_date || ''],
      planned_end_date: [this.stage.planned_end_date || ''],
      value: [this.stage.value || 0],
      status: [this.stage.status || 'pending'],
      specific_data: this.fb.group({})
    });
    // Preenche campos do escopo dinamicamente
    if (this.stage.specific_data) {
      this.escopoKeys = Object.keys(this.stage.specific_data);
      this.escopoKeys.forEach(key => {
        (this.form.get('specific_data') as FormGroup).addControl(key, this.fb.control(this.stage.specific_data[key]));
      });
    }
  }

  onSubmit() {
    if (this.form.valid) {
      this.save.emit(this.form.value);
    }
  }
}
