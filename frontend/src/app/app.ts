import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PeopleTable } from "./people-table/people-table";

@Component({
  selector: 'app-root',
  imports: [PeopleTable],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected title = 'strichliste';
}
