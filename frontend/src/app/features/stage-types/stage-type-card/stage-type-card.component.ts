import { Component, Input, Output, EventEmitter } from '@angular/core';
import {SharedModule} from "../../../shared/shared.module";
import {StageType} from "../../../core/models/stage-type.model";


@Component({
  selector: 'app-stage-type-card',
  standalone: true,
  templateUrl: './stage-type-card.component.html',
  styleUrls: ['./stage-type-card.component.scss'],
  imports: [SharedModule]
})
export class StageTypeCardComponent {
  @Input() stageType!: StageType;
  @Output() view = new EventEmitter<string>();
  @Output() edit = new EventEmitter<string>();
  @Output() delete = new EventEmitter<StageType>();

  onView(): void {
    this.view.emit(this.stageType.id);
  }

  onEdit(): void {
    this.edit.emit(this.stageType.id);
  }

  onDelete(): void {
    this.delete.emit(this.stageType);
  }
}
